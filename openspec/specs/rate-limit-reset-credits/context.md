## Operational finding

A native request on a weekly-only business account returned `nothing_to_reset`, zero windows reset, and the selected credit still available despite nonzero weekly usage. Team accounts showed actual short/weekly quota resets. Unchanged usage alone cannot distinguish a provider no-op from a transport error. The application must expose the returned outcome rather than infer consumption from an attempt record.

Example: HTTP 200 `{code: "nothing_to_reset", credit: {id: "credit-a", status: "available"}, windows_reset: 0}` is a confirmed unused attempt; HTTP 200 `{code: "no_credit", credit: null, windows_reset: 0}` is a valid no-credit result.
