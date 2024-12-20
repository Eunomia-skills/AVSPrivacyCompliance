USE [AVSPrivacyCompliance]
GO
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[PrivacyPolicyExtractRealTime](
	[skill_id] [nvarchar](150) NULL,
	[entity] [nvarchar](50) NULL,
	[verb] [nvarchar](50) NULL,
	[object] [nvarchar](150) NULL,
	[original_verb] [nvarchar](50) NULL,
	[sentence] [nvarchar](max) NULL,
	[privacy_label] [varchar](50) NULL,
	[label_type] [varchar](50) NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
