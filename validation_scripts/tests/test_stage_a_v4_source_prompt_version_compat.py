from __future__ import annotations

import hashlib
import unittest
from pathlib import Path

from validation_scripts import stage_a_full_v3_completeness_review4945668766 as mod


class TestStageAV4SourcePromptVersionCompatibility(unittest.TestCase):
    def base(self):
        path = Path('docs/llm_prompts/v1/01_PROMPT_0_1_Stage_A.md')
        return {
            'source_prompt_file': str(path),
            'source_prompt_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'source_prompt_authority': 'uploaded_or_repo_source_file_prompt',
            'source_prompt_provenance_status': 'PASS',
            'strict_passed_spec': [],
            'candidate_review_pool': [],
            'watchlist_context_pool': [],
            'reject_or_support_only_pool': [],
        }

    def messages(self, data):
        out=[]
        mod._validate_source_prompt_provenance(data,out)
        return out

    def test_historical_v3_artifact_keeps_historical_version(self):
        data=self.base(); data['source_prompt_version']=mod._SOURCE_PROMPT_VERSION
        self.assertEqual(self.messages(data),[])

    def test_v4_candidate_requires_active_v4_prompt_version(self):
        data=self.base(); data['strict_passed_spec']=[{'selection_policy_version':mod._V4_POLICY_VERSION}]
        data['source_prompt_version']=mod._SOURCE_PROMPT_V4_VERSION
        self.assertEqual(self.messages(data),[])
        data['source_prompt_version']=mod._SOURCE_PROMPT_VERSION
        self.assertTrue(any(mod._SOURCE_PROMPT_V4_VERSION in m for m in self.messages(data)))

    def test_v4_review_only_artifact_also_requires_v4_version(self):
        data=self.base(); data['candidate_review_pool']=[{'selection_policy_version':mod._V4_POLICY_VERSION}]
        data['source_prompt_version']=mod._SOURCE_PROMPT_V4_VERSION
        self.assertEqual(self.messages(data),[])


if __name__ == '__main__':
    unittest.main()
