USE [AVSPrivacyCompliance]
GO
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[skilldetails](
	[skill_name] [nvarchar](255) NULL,
	[skill_ASIN] [nvarchar](255) NULL,
	[skill_id] [nvarchar](255) NULL,
	[policy_hash] [nvarchar](255) NULL
) ON [PRIMARY]
GO
