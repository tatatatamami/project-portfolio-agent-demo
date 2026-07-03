using System.Collections.Concurrent;
using System.Net.Http.Headers;
using System.Text;
using System.Text.Json;
using Azure.Core;
using Microsoft.Extensions.Options;

namespace ServicePortfolio.Dashboard.Services;

public sealed class FoundryAgentHttpClient : IFoundryAgentClient
{
    private readonly HttpClient _httpClient;
    private readonly TokenCredential _credential;
    private readonly FoundryAgentOptions _options;
    private readonly ILogger<FoundryAgentHttpClient> _logger;
    private readonly SemaphoreSlim _tokenLock = new(1, 1);
    private AccessToken? _cachedToken;

    public FoundryAgentHttpClient(
        HttpClient httpClient,
        TokenCredential credential,
        IOptions<FoundryAgentOptions> options,
        ILogger<FoundryAgentHttpClient> logger)
    {
        _httpClient = httpClient;
        _credential = credential;
        _options = options.Value;
        _logger = logger;
        _httpClient.Timeout = TimeSpan.FromSeconds(Math.Max(_options.TimeoutSeconds, 10));
    }

    public async Task<string> SendMessageAsync(
        string conversationId,
        string message,
        CancellationToken cancellationToken = default)
    {
        var agentName = ResolveAgentName();
        var response = await SendJsonAsync(HttpMethod.Post, "openai/v1/responses", new
        {
            agent_reference = new
            {
                type = "agent_reference",
                name = agentName
            },
            input = message
        }, cancellationToken);

        return ExtractResponseText(response);
    }

    private string ResolveAgentName()
    {
        if (!string.IsNullOrWhiteSpace(_options.AgentName))
        {
            return _options.AgentName;
        }

        if (!string.IsNullOrWhiteSpace(_options.AgentId) && !_options.AgentId.StartsWith("asst_", StringComparison.OrdinalIgnoreCase))
        {
            return _options.AgentId;
        }

        throw new InvalidOperationException("Foundry AgentName must be set for the Responses API client.");
    }

    private async Task<JsonDocument> SendJsonAsync(
        HttpMethod method,
        string relativePath,
        object? body,
        CancellationToken cancellationToken)
    {
        using var request = new HttpRequestMessage(method, BuildUri(relativePath));
        var token = await GetAccessTokenAsync(cancellationToken);
        request.Headers.Authorization = new AuthenticationHeaderValue("Bearer", token);

        if (body is not null)
        {
            request.Content = new StringContent(JsonSerializer.Serialize(body), Encoding.UTF8, "application/json");
        }

        using var response = await _httpClient.SendAsync(request, cancellationToken);
        var content = await response.Content.ReadAsStringAsync(cancellationToken);
        if (!response.IsSuccessStatusCode)
        {
            throw new HttpRequestException($"Foundry Agent request failed with {(int)response.StatusCode}: {content}");
        }

        return JsonDocument.Parse(string.IsNullOrWhiteSpace(content) ? "{}" : content);
    }

    private Uri BuildUri(string relativePath)
    {
        var baseEndpoint = _options.ProjectEndpoint.TrimEnd('/');
        if (relativePath.TrimStart('/').StartsWith("openai/v1/", StringComparison.OrdinalIgnoreCase))
        {
            return new Uri($"{baseEndpoint}/{relativePath.TrimStart('/')}");
        }

        var separator = relativePath.Contains('?', StringComparison.Ordinal) ? "&" : "?";
        return new Uri($"{baseEndpoint}/{relativePath.TrimStart('/')}{separator}api-version={Uri.EscapeDataString(_options.ApiVersion)}");
    }

    private async Task<string> GetAccessTokenAsync(CancellationToken cancellationToken)
    {
        if (_cachedToken is { } cachedToken && cachedToken.ExpiresOn > DateTimeOffset.UtcNow.AddMinutes(5))
        {
            return cachedToken.Token;
        }

        await _tokenLock.WaitAsync(cancellationToken);
        try
        {
            if (_cachedToken is { } refreshedToken && refreshedToken.ExpiresOn > DateTimeOffset.UtcNow.AddMinutes(5))
            {
                return refreshedToken.Token;
            }

            _cachedToken = await _credential.GetTokenAsync(new TokenRequestContext([_options.TokenScope]), cancellationToken);
            return _cachedToken.Value.Token;
        }
        finally
        {
            _tokenLock.Release();
        }
    }

    private static string ExtractResponseText(JsonDocument response)
    {
        if (response.RootElement.TryGetProperty("output_text", out var outputText)
            && outputText.ValueKind == JsonValueKind.String
            && !string.IsNullOrWhiteSpace(outputText.GetString()))
        {
            return outputText.GetString()!;
        }

        if (!response.RootElement.TryGetProperty("output", out var output) || output.ValueKind != JsonValueKind.Array)
        {
            throw new InvalidOperationException("Foundry Agent response did not contain output.");
        }

        var builder = new StringBuilder();
        foreach (var message in output.EnumerateArray())
        {
            var type = message.TryGetProperty("type", out var typeElement) ? typeElement.GetString() : null;
            if (!string.Equals(type, "message", StringComparison.OrdinalIgnoreCase))
            {
                continue;
            }

            if (!message.TryGetProperty("content", out var content) || content.ValueKind != JsonValueKind.Array)
            {
                continue;
            }

            foreach (var item in content.EnumerateArray())
            {
                if (item.TryGetProperty("type", out var itemType)
                    && string.Equals(itemType.GetString(), "output_text", StringComparison.OrdinalIgnoreCase)
                    && item.TryGetProperty("text", out var text)
                    && text.ValueKind == JsonValueKind.String)
                {
                    builder.AppendLine(text.GetString());
                }
                else if (item.TryGetProperty("text", out var plainText) && plainText.ValueKind == JsonValueKind.String)
                {
                    builder.AppendLine(plainText.GetString());
                }
            }
        }

        var answer = builder.ToString().Trim();
        if (!string.IsNullOrWhiteSpace(answer))
        {
            return answer;
        }

        throw new InvalidOperationException("Foundry Agent did not return output text.");
    }

    private static string RequiredString(JsonDocument document, string propertyName)
    {
        return RequiredString(document.RootElement, propertyName);
    }

    private static string RequiredString(JsonElement element, string propertyName)
    {
        if (element.TryGetProperty(propertyName, out var property) && !string.IsNullOrWhiteSpace(property.GetString()))
        {
            return property.GetString()!;
        }

        throw new InvalidOperationException($"Foundry Agent response did not contain '{propertyName}'.");
    }
}