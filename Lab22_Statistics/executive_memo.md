# Executive Memo

- Date: 2026-06-04
- Analyst: Codex
- Dataset used: marketing_campaign_dataset_original.csv
- Period analyzed: 2021-01-01 to 2021-12-31

## Executive Summary
No CPA or conversion-rate channel pairs remained statistically significant after FDR correction. The channels are broadly similar on the metrics tested, so the main decision lever is relative efficiency rather than a single clearly dominant channel.

## Key Findings
### Top Performing Channels
| Channel_Used | Composite_Score | Allocation_Percentage | Priority |
| --- | --- | --- | --- |
| Website | 0.90 | 30.00 | Increase investment |
| Facebook | 0.80 | 26.67 | Increase investment |
| Email | 0.50 | 16.67 | Maintain |

### Statistically Significant Differences
No CPA or conversion-rate differences survived FDR correction.

### Confidence Intervals for CPA
| Channel_Used | Mean_CPA | CI_Lower | CI_Upper |
| --- | --- | --- | --- |
| Website | 283.61 | 281.37 | 286.23 |
| Email | 285.08 | 282.67 | 287.58 |
| Facebook | 285.57 | 283.33 | 288.04 |
| YouTube | 286.46 | 283.79 | 288.93 |
| Google Ads | 286.79 | 284.48 | 289.12 |
| Instagram | 286.94 | 284.33 | 289.83 |

### Data Adequacy and Power
#### Power Curves
| effect_size_pct | n_days | power |
| --- | --- | --- |
| 5.000 | 30.000 | 0.243 |
| 5.000 | 60.000 | 0.416 |
| 5.000 | 90.000 | 0.601 |
| 5.000 | 120.000 | 0.715 |
| 5.000 | 180.000 | 0.901 |
| 10.000 | 30.000 | 0.707 |
| 10.000 | 60.000 | 0.952 |
| 10.000 | 90.000 | 0.998 |
| 10.000 | 120.000 | 0.998 |
| 10.000 | 180.000 | 1.000 |
| 15.000 | 30.000 | 0.963 |
| 15.000 | 60.000 | 1.000 |
| 15.000 | 90.000 | 1.000 |
| 15.000 | 120.000 | 1.000 |
| 15.000 | 180.000 | 1.000 |
| 20.000 | 30.000 | 1.000 |
| 20.000 | 60.000 | 1.000 |
| 20.000 | 90.000 | 1.000 |
| 20.000 | 120.000 | 1.000 |
| 20.000 | 180.000 | 1.000 |

#### Minimum Sample Size for 80% Power
| Effect_Size_Pct | Minimum_Days_For_80Pct | Power_At_Min_Days | Status_At_90_Days | Additional_Days_Needed |
| --- | --- | --- | --- | --- |
| 5.00 | 138.00 | 0.81 | insufficient | 48.00 |
| 10.00 | 34.00 | 0.84 | sufficient | 0.00 |
| 15.00 | 17.00 | 0.81 | sufficient | 0.00 |
| 20.00 | 11.00 | 0.82 | sufficient | 0.00 |

The current benchmark uses 90 days of data, while the dataset contains 365 daily observations per channel.

## Recommendations
Prioritize channels with the highest composite score, and reduce emphasis on channels in the bottom tier.
Allocate resources proportionally to the composite score below.

| Channel_Used | Composite_Score | Allocation_Percentage | Priority |
| --- | --- | --- | --- |
| Website | 0.90 | 30.00 | Increase investment |
| Facebook | 0.80 | 26.67 | Increase investment |
| Email | 0.50 | 16.67 | Maintain |
| YouTube | 0.40 | 13.33 | Maintain |
| Google Ads | 0.30 | 10.00 | Deprioritize |
| Instagram | 0.10 | 3.33 | Deprioritize |

## Statistical Caveats
- Conversions were estimated from clicks and conversion rate because the source file did not include a raw binary conversion flag.
- Multiple comparisons correction was applied to CPA and conversion-rate pairwise tests.
- Bootstrap confidence intervals capture sampling variability, but they do not remove model or measurement bias.
- Statistical significance does not necessarily imply practical significance.
- Power estimates are simulation-based and depend on the assumed variance structure.

## Next Steps
- Re-run the analysis after new campaign data arrives to see whether the composite ranking changes.
- Test whether channel-specific creative or audience segments explain the small differences observed here.
- If budget changes are possible, bias incremental spend toward the top-ranked channels and monitor CPA and ROAS weekly.