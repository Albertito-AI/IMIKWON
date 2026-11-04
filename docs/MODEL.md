# Model integration and sources

Source check: 5 November 2026, Singapore time.

| Claim or integration choice | Primary source |
| --- | --- |
| K3.1 Pro announced; API access available; downloadable weights promised by 4 November | [Moonshot announcement](https://www.kimi.com/en/blog/kimi-k3-1-pro) |
| Model ID, endpoint, output limits, reasoning and structured output | [K3.1 Pro API guide](https://platform.kimi.ai/docs/guide/kimi-k3-1-pro-quickstart) |
| Current headline model prices | [Kimi API Platform](https://platform.kimi.ai/) |
| Cache write and usage billing | [Pricing](https://platform.kimi.ai/docs/pricing/chat) and [cache guide](https://platform.kimi.ai/docs/guide/context-caching) |
| Published price breakdown including one-hour cache writes | [Kimi pricing explanation](https://www.kimi.ai/resources/kimi-k3-1-pro-pricing) |

The documented API accepts `kimi-k3.1-pro` and `kimi-k3.1-pro-highspeed`. IMIKWON defaults to the standard model. It sets `reasoning_effort` and `max_completion_tokens`, omits fixed sampling parameters, and requests JSON Schema output. The second call returns the complete first assistant message unchanged, including `reasoning_content`, as required by Kimi. This compatibility is covered by mocked tests; a successful live request remains an acceptance gate.

Moonshot's announced benchmarks are upstream vendor results. They do not establish IMIKWON's coding success rate. No comparative quality ranking is made here.

We could not verify a downloadable K3.1 Pro checkpoint together with its exact licence during this launch. The announcement alone does not establish that release. The previous K3 licence must not be assumed to govern K3.1 Pro. IMIKWON distributes only its own MIT-licensed client code. API access remains subject to the provider's terms and charges.

Self-hosting a multi-trillion-parameter model is not represented as a laptop feature or a zero-cost option. An HTTPS-compatible endpoint can be configured, but the hardware requirements, upstream licence and server compatibility need separate verification.

IMIKWON is independent of Moonshot AI and has no claimed affiliation or endorsement.
