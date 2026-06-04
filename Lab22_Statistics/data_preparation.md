# Data Preparation Report

## Transformations Applied
- Standardized column names by stripping leading and trailing spaces.
- Removed duplicate rows and duplicate `Campaign_ID` values.
- Converted `Date` to datetime and kept the original row order.
- Extracted numeric values from `Duration` and stored them as days.
- Cleaned `Acquisition_Cost` by removing currency symbols and commas.
- Coerced numeric fields to numeric types: `Conversion_Rate`, `ROI`, `Clicks`, `Impressions`, and `Engagement_Score`.
- Removed negative values, invalid engagement scores, invalid dates, and rows where `Clicks > Impressions`.
- Created derived metrics: `CTR`, `Estimated_Conversions`, and `CPA`.

## Row Counts
- Raw rows: 200,000
- Cleaned rows: 200,000

## Column Summary Statistics
### Company
- Number of groups: 5

| Group | Sample Size |
| --- | ---: |
| TechCorp | 40,237 |
| Alpha Innovations | 40,051 |
| DataTech Solutions | 40,012 |
| NexGen Systems | 39,991 |
| Innovate Industries | 39,709 |

### Campaign_Type
- Number of groups: 5

| Group | Sample Size |
| --- | ---: |
| Influencer | 40,169 |
| Search | 40,157 |
| Display | 39,987 |
| Email | 39,870 |
| Social Media | 39,817 |

### Target_Audience
- Number of groups: 5

| Group | Sample Size |
| --- | ---: |
| Men 18-24 | 40,258 |
| Men 25-34 | 40,023 |
| All Ages | 40,019 |
| Women 25-34 | 40,013 |
| Women 35-44 | 39,687 |

### Channel_Used
- Number of groups: 6

| Group | Sample Size |
| --- | ---: |
| Email | 33,599 |
| Google Ads | 33,438 |
| YouTube | 33,392 |
| Instagram | 33,392 |
| Website | 33,360 |
| Facebook | 32,819 |

### Location
- Number of groups: 5

| Group | Sample Size |
| --- | ---: |
| Miami | 40,269 |
| New York | 40,024 |
| Chicago | 40,010 |
| Los Angeles | 39,947 |
| Houston | 39,750 |

### Language
- Number of groups: 5

| Group | Sample Size |
| --- | ---: |
| Mandarin | 40,255 |
| Spanish | 40,102 |
| German | 39,983 |
| English | 39,896 |
| French | 39,764 |

### Customer_Segment
- Number of groups: 5

| Group | Sample Size |
| --- | ---: |
| Foodies | 40,208 |
| Tech Enthusiasts | 40,151 |
| Outdoor Adventurers | 40,011 |
| Health & Wellness | 39,888 |
| Fashionistas | 39,742 |

### Date
- Number of groups: 365 unique days
- Data range: 2021-01-01 to 2021-12-31

### Campaign_ID
- Number of groups: discrete numeric values
- Data range: 1 to 200,000

### Duration
- Number of groups: discrete numeric values
- Data range: 15 to 60

### Conversion_Rate
- Number of groups: continuous numeric values
- Data range: 0.0100 to 0.1500

### Acquisition_Cost
- Number of groups: continuous numeric values
- Data range: 5,000.0000 to 20,000.0000

### ROI
- Number of groups: continuous numeric values
- Data range: 2.0000 to 8.0000

### Clicks
- Number of groups: discrete numeric values
- Data range: 100 to 1,000

### Impressions
- Number of groups: discrete numeric values
- Data range: 1,000 to 10,000

### Engagement_Score
- Number of groups: discrete numeric values
- Data range: 1 to 10

### CTR
- Number of groups: continuous numeric values
- Data range: 0.0101 to 0.9920

### Estimated_Conversions
- Number of groups: continuous numeric values
- Data range: 1.0000 to 150.0000

### CPA
- Number of groups: continuous numeric values
- Data range: 34.2178 to 19,432.3529
