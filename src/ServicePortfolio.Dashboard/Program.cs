using ServicePortfolio.Dashboard.Components;
using ServicePortfolio.Dashboard.Services;
using Azure.Core;
using Azure.Identity;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddRazorComponents()
    .AddInteractiveServerComponents();

builder.Services.AddScoped<IDashboardDataService, JsonDashboardDataService>();
builder.Services.Configure<FoundryAgentOptions>(builder.Configuration.GetSection("FoundryAgent"));
builder.Services.AddSingleton<TokenCredential>(_ => builder.Environment.IsDevelopment()
    ? new AzureCliCredential()
    : new DefaultAzureCredential());

if (string.Equals(builder.Configuration["AgentChat:Provider"], "Foundry", StringComparison.OrdinalIgnoreCase))
{
    builder.Services.AddHttpClient<IFoundryAgentClient, FoundryAgentHttpClient>();
    builder.Services.AddScoped<IAgentChatService, FoundryAgentChatService>();
}
else
{
    builder.Services.AddScoped<IAgentChatService, FakeAgentChatService>();
}

var app = builder.Build();

if (!app.Environment.IsDevelopment())
{
    app.UseExceptionHandler("/Error", createScopeForErrors: true);
    app.UseHsts();
}

app.UseHttpsRedirection();
app.UseStaticFiles();
app.UseAntiforgery();

app.MapRazorComponents<App>()
    .AddInteractiveServerRenderMode();

app.Run();
