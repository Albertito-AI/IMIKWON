# Costs you can inspect

IMIKWON is free software. Model inference is paid directly to the user's provider. There is no bundled allowance, subscription, markup or claim of guaranteed savings.

## Price snapshot

Checked 5 November 2026, Singapore time, against the [official API homepage](https://platform.kimi.ai/) and [Kimi's pricing explanation](https://www.kimi.ai/resources/kimi-k3-1-pro-pricing). The [API pricing documentation](https://platform.kimi.ai/docs/pricing/chat) explains billing and cache-write charges.

USD per million tokens, before tax:

| Standard K3.1 Pro item | Published rate |
| --- | ---: |
| Uncached input | $2.00 |
| Cached input | $0.20 |
| Five-minute cache write | $2.00 |
| One-hour cache write | $4.00 |
| Output | $10.00 |

Prices can change. Highspeed has different rates. Do not reuse these settings for another model or provider without checking its billable components. IMIKWON requires explicit rates rather than silently relying on an ageing price table.

For example, 10,000 uncached input tokens, 10,000 five-minute cache-write tokens and 2,000 output tokens total **$0.06**, before taxes. This is arithmetic using assumed usage, not a measured IMIKWON task or promise about reasoning length. Reasoning consumes output tokens too.

## Local admission control

Before each request, the program reserves:

```text
input allowance = UTF-8 bytes of the full request JSON + 4,096
reserve = (input allowance × input ceiling + output token cap × output price) / 1,000,000
```

The input ceiling must cover the greater of uncached/cached input rates **plus the maximum cache-write rate that could apply**. For this snapshot, `--input-ceiling 6 --output-price 10` uses the higher one-hour write rate even though the request leaves the provider's default TTL unchanged.

UTF-8 bytes plus an overhead margin intentionally overestimates ordinary text token counts. This is not a tokenizer proof, a provider-side hard cap or a contractual bill limit. Incorrect prices, provider accounting differences, taxes, parallel processes and in-flight requests can defeat a local dollar estimate. Use the provider's spending controls as well. Each CLI invocation has a separate budget; there is no shared monthly ledger.

Reservations accumulate across both calls and are never released based on a guessed cache discount. No automatic retry is performed after errors or timeouts. Provider-reported usage is stored without reinterpreting unknown billing fields. A failed request may still be billed; the cost record retains its reservation.

The record in `.imikwon/JOB.cost.json` contains the configured rates, local reservations and provider-reported usage. It does not contain the API key, task, source or reasoning. Proposals contain generated code and local paths; keep the entire `.imikwon/` directory out of public commits.

## Reducing cost while checking quality

Start with a small source file and its test. Inspect the scope before transmission. Use a concise, testable task. Try `--single-pass --effort low --max-output 4096` on a small task, understanding that lower limits may produce an incomplete response. For more difficult work retain the default review pass and use enough output budget for reasoning plus the complete replacement files.

Stable request prefixes permit provider caching, but IMIKWON does not promise a cache hit. Batch inference and exact token-count API calls are not implemented in this alpha. Compare **cost per successfully tested task**, rather than token price alone, before claiming savings.
