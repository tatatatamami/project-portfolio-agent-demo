namespace ServicePortfolio.Dashboard.Models;

public enum ChatRole { User, Assistant }

public sealed class ChatMessage
{
    public required ChatRole Role { get; init; }
    public string Content { get; set; } = string.Empty;
    public DateTimeOffset Timestamp { get; init; } = DateTimeOffset.UtcNow;
    public bool IsStreaming { get; set; }
    public string? Error { get; set; }
}
