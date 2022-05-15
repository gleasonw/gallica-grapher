from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

DEFAULT_TIMEOUT = 25  # seconds


class TimeoutAndRetryHTTPAdapter(HTTPAdapter):
	def __init__(self, *args, **kwargs):
		retryStrategy = Retry(
			total=10,
			status_forcelist=[413, 429, 500, 502, 503, 504],
			method_whitelist=["HEAD", "GET", "OPTIONS", "PUT", "DELETE"],
			backoff_factor=2
		)
		self.timeout = DEFAULT_TIMEOUT
		if "timeout" in kwargs:
			self.timeout = kwargs["timeout"]
			del kwargs["timeout"]
		super().__init__(*args, **kwargs, max_retries=retryStrategy, pool_maxsize=50)

	def send(self, request, **kwargs):
		timeout = kwargs.get("timeout")
		if timeout is None:
			kwargs["timeout"] = self.timeout
		return super().send(request, **kwargs)