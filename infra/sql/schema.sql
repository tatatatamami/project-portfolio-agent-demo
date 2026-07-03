-- Service Portfolio Azure SQL schema for Foundry Azure SQL MCP Server.
-- Source of truth for structured facts used by service-portfolio-chat-agent-vnext.

create table dbo.Customers (
    CustomerID nvarchar(32) not null primary key,
    CustomerName nvarchar(200) not null,
    Industry nvarchar(100) null,
    Region nvarchar(100) null,
    Segment nvarchar(100) null,
    KnowledgeStatus nvarchar(50) null
);

go

create table dbo.Projects (
    ProjectID nvarchar(32) not null primary key,
    CustomerID nvarchar(32) null,
    ProjectName nvarchar(300) not null,
    Industry nvarchar(100) null,
    ProjectTheme nvarchar(200) null,
    StartDate date null,
    EndDate date null,
    Status nvarchar(100) null,
    WinLoss nvarchar(50) null,
    KnowledgeStatus nvarchar(50) null,
    constraint FK_Projects_Customers foreign key (CustomerID) references dbo.Customers(CustomerID)
);

go

create table dbo.Opportunities (
    OpportunityID nvarchar(64) not null primary key,
    CustomerID nvarchar(32) null,
    ProjectID nvarchar(32) null,
    OpportunityName nvarchar(300) null,
    Stage nvarchar(100) null,
    AmountJPYMillion decimal(18,2) null,
    WinLoss nvarchar(50) null,
    CloseDate date null,
    KnowledgeStatus nvarchar(50) null
);

go

create table dbo.Proposals (
    ProposalID nvarchar(64) not null primary key,
    ProjectID nvarchar(32) null,
    ProposalType nvarchar(200) null,
    ProposalTheme nvarchar(200) null,
    KeyMessage nvarchar(max) null,
    Differentiator nvarchar(max) null,
    Result nvarchar(50) null,
    KnowledgeStatus nvarchar(50) null
);

go

create table dbo.ProjectFinancials (
    ProjectID nvarchar(32) not null primary key,
    RevenueJPYMillion decimal(18,2) null,
    CostJPYMillion decimal(18,2) null,
    ProfitJPYMillion decimal(18,2) null,
    ProfitMarginPct decimal(9,2) null,
    EffortPersonMonths decimal(9,2) null,
    EffortReductionPct decimal(9,2) null,
    FinancialStatus nvarchar(50) null,
    KnowledgeStatus nvarchar(50) null,
    constraint FK_ProjectFinancials_Projects foreign key (ProjectID) references dbo.Projects(ProjectID)
);

go

create table dbo.Requirements (
    RequirementID nvarchar(64) not null primary key,
    ProjectID nvarchar(32) null,
    Category nvarchar(100) null,
    RequirementName nvarchar(300) null,
    Description nvarchar(max) null,
    Priority nvarchar(50) null,
    KnowledgeStatus nvarchar(50) null
);

go

create table dbo.Features (
    FeatureID nvarchar(64) not null primary key,
    ProjectID nvarchar(32) null,
    FeatureName nvarchar(300) null,
    Category nvarchar(100) null,
    Description nvarchar(max) null,
    DeliveryStatus nvarchar(100) null,
    KnowledgeStatus nvarchar(50) null
);

go

create table dbo.Risks (
    RiskID nvarchar(64) not null primary key,
    ProjectID nvarchar(32) null,
    Category nvarchar(100) null,
    RiskName nvarchar(300) null,
    Description nvarchar(max) null,
    Severity nvarchar(50) null,
    Status nvarchar(100) null,
    Mitigation nvarchar(max) null,
    KnowledgeStatus nvarchar(50) null
);

go

create table dbo.BusinessOutcomes (
    OutcomeID nvarchar(64) not null primary key,
    ProjectID nvarchar(32) null,
    OutcomeType nvarchar(100) null,
    MetricName nvarchar(200) null,
    BeforeValue decimal(18,2) null,
    AfterValue decimal(18,2) null,
    Unit nvarchar(50) null,
    ImprovementPct decimal(9,2) null,
    OutcomeStatus nvarchar(100) null,
    Description nvarchar(max) null,
    KnowledgeStatus nvarchar(50) null
);

go

create table dbo.Documents (
    SourceID nvarchar(100) not null primary key,
    ProjectID nvarchar(32) null,
    DocumentType nvarchar(100) null,
    Title nvarchar(300) null,
    SourcePath nvarchar(500) null,
    KnowledgeStatus nvarchar(50) null,
    SearchIndexName nvarchar(100) not null default 'project-knowledge-index'
);

go

create table dbo.ServiceCandidates (
    CandidateID nvarchar(64) not null primary key,
    Rank int not null,
    Name nvarchar(300) not null,
    ExecutiveSummary nvarchar(max) null,
    BusinessReason nvarchar(max) null,
    CurrentBusinessModel nvarchar(100) null,
    NextBusinessModel nvarchar(100) null,
    FutureBusinessModel nvarchar(100) null,
    BusinessModelRationale nvarchar(max) null,
    RawJson nvarchar(max) null
);

go

create table dbo.CandidateScores (
    CandidateID nvarchar(64) not null primary key,
    PriorityScore int null,
    Profitability int null,
    Reusability int null,
    Standardization int null,
    RecurringRevenue int null,
    SaasReadiness int null,
    Feasibility int null,
    Confidence int null,
    constraint FK_CandidateScores_Candidates foreign key (CandidateID) references dbo.ServiceCandidates(CandidateID)
);

go

create table dbo.CandidateMetrics (
    CandidateID nvarchar(64) not null primary key,
    SupportingProjectCount int null,
    IndustryCount int null,
    WinRate decimal(9,2) null,
    AverageMarginRate decimal(9,2) null,
    AverageEffortReductionRate decimal(9,2) null,
    WonRevenue decimal(18,2) null,
    constraint FK_CandidateMetrics_Candidates foreign key (CandidateID) references dbo.ServiceCandidates(CandidateID)
);

go

create table dbo.CandidateIceAxes (
    CandidateID nvarchar(64) not null,
    AxisName nvarchar(32) not null,
    Score int null,
    Summary nvarchar(max) null,
    CalculationMethod nvarchar(100) null,
    FormulaVersion nvarchar(100) null,
    constraint PK_CandidateIceAxes primary key (CandidateID, AxisName),
    constraint FK_CandidateIceAxes_Candidates foreign key (CandidateID) references dbo.ServiceCandidates(CandidateID)
);

go

create table dbo.CandidateIceFactors (
    CandidateID nvarchar(64) not null,
    AxisName nvarchar(32) not null,
    FactorOrder int not null,
    FactorName nvarchar(200) null,
    FactorValue nvarchar(100) null,
    Contribution decimal(9,2) null,
    constraint PK_CandidateIceFactors primary key (CandidateID, AxisName, FactorOrder)
);

go

create table dbo.CandidateSupportingProjects (
    CandidateID nvarchar(64) not null,
    ProjectID nvarchar(32) not null,
    ProjectName nvarchar(300) null,
    Industry nvarchar(100) null,
    EvidenceSummary nvarchar(max) null,
    SourceIDs nvarchar(max) null,
    constraint PK_CandidateSupportingProjects primary key (CandidateID, ProjectID)
);

go

create table dbo.CandidateReusableAssets (
    CandidateID nvarchar(64) not null,
    AssetName nvarchar(200) not null,
    AssetType nvarchar(100) null,
    OccurrenceCount int null,
    TotalProjectCount int null,
    ReadinessScore int null,
    CurrentState nvarchar(max) null,
    NextAction nvarchar(max) null,
    SourceIDs nvarchar(max) null,
    constraint PK_CandidateReusableAssets primary key (CandidateID, AssetName)
);

go

create table dbo.CandidateStandardizationGaps (
    CandidateID nvarchar(64) not null,
    GapOrder int not null,
    Category nvarchar(100) null,
    CurrentState nvarchar(max) null,
    TargetState nvarchar(max) null,
    Priority nvarchar(50) null,
    Effort nvarchar(50) null,
    Dependency nvarchar(max) null,
    SourceIDs nvarchar(max) null,
    constraint PK_CandidateStandardizationGaps primary key (CandidateID, GapOrder)
);

go

create table dbo.CandidateRisks (
    CandidateID nvarchar(64) not null,
    RiskOrder int not null,
    RiskName nvarchar(200) null,
    Impact nvarchar(50) null,
    Likelihood nvarchar(50) null,
    Mitigation nvarchar(max) null,
    SourceIDs nvarchar(max) null,
    constraint PK_CandidateRisks primary key (CandidateID, RiskOrder)
);

go

create table dbo.CandidateManagementDecisions (
    CandidateID nvarchar(64) not null primary key,
    Decision nvarchar(max) null,
    InvestmentLevel nvarchar(100) null,
    TimeHorizon nvarchar(100) null,
    SourceIDs nvarchar(max) null
);

go

create table dbo.CandidateDecisionItems (
    CandidateID nvarchar(64) not null,
    ItemType nvarchar(50) not null,
    ItemOrder int not null,
    ItemText nvarchar(max) null,
    SourceIDs nvarchar(max) null,
    constraint PK_CandidateDecisionItems primary key (CandidateID, ItemType, ItemOrder)
);

go

create index IX_Projects_ProjectTheme on dbo.Projects(ProjectTheme);
create index IX_Projects_WinLoss on dbo.Projects(WinLoss);
create index IX_ServiceCandidates_Rank on dbo.ServiceCandidates(Rank);
create index IX_Documents_ProjectID on dbo.Documents(ProjectID);

go

create or alter view dbo.vTopCandidates as
select
    c.Rank,
    c.CandidateID,
    c.Name,
    s.PriorityScore as IceScore,
    m.WinRate,
    m.AverageMarginRate,
    m.WonRevenue,
    m.SupportingProjectCount,
    m.IndustryCount,
    s.SaasReadiness,
    c.CurrentBusinessModel,
    c.NextBusinessModel,
    c.FutureBusinessModel
from dbo.ServiceCandidates c
left join dbo.CandidateScores s on c.CandidateID = s.CandidateID
left join dbo.CandidateMetrics m on c.CandidateID = m.CandidateID;

go

create or alter view dbo.vCandidateIceBreakdown as
select
    c.Rank,
    c.CandidateID,
    c.Name as CandidateName,
    s.PriorityScore as IceScore,
    a.AxisName,
    a.Score as AxisScore,
    a.Summary,
    f.FactorOrder,
    f.FactorName,
    f.FactorValue,
    f.Contribution
from dbo.ServiceCandidates c
join dbo.CandidateScores s on c.CandidateID = s.CandidateID
join dbo.CandidateIceAxes a on c.CandidateID = a.CandidateID
left join dbo.CandidateIceFactors f on a.CandidateID = f.CandidateID and a.AxisName = f.AxisName;

go

create or alter view dbo.vCandidateEvidenceProjects as
select
    c.Rank,
    c.CandidateID,
    c.Name as CandidateName,
    p.ProjectID,
    p.ProjectName,
    p.Industry,
    p.EvidenceSummary,
    p.SourceIDs
from dbo.ServiceCandidates c
join dbo.CandidateSupportingProjects p on c.CandidateID = p.CandidateID;

go

create or alter view dbo.vCandidateSaasGaps as
select
    c.Rank,
    c.CandidateID,
    c.Name as CandidateName,
    g.GapOrder,
    g.Category,
    g.CurrentState,
    g.TargetState,
    g.Priority,
    g.Effort,
    g.Dependency,
    g.SourceIDs
from dbo.ServiceCandidates c
join dbo.CandidateStandardizationGaps g on c.CandidateID = g.CandidateID;

go

create or alter view dbo.vCandidate90DayDecisions as
select
    c.Rank,
    c.CandidateID,
    c.Name as CandidateName,
    d.Decision,
    d.InvestmentLevel,
    d.TimeHorizon,
    i.ItemType,
    i.ItemOrder,
    i.ItemText,
    i.SourceIDs
from dbo.ServiceCandidates c
left join dbo.CandidateManagementDecisions d on c.CandidateID = d.CandidateID
left join dbo.CandidateDecisionItems i on c.CandidateID = i.CandidateID;
