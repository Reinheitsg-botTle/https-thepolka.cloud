import unittest
from agents.security_agent import SecurityBarbie
class SecurityBoundaryTests(unittest.TestCase):
 def test_rejects_unapproved_host(self):
  with self.assertRaises(PermissionError):SecurityBarbie()._target("https://example.com")
 def test_adds_https(self):self.assertTrue(SecurityBarbie()._target("agent.thepolka.cloud").startswith("https://"))
if __name__=="__main__":unittest.main()
