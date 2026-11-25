import unittest
import os
import re


def extract_relative_links(md_content):
    # Regex for markdown links: [text](path) excluding external URLs
    pattern = r'\[.*?\]\((?!https?://|mailto:)(.*?)\)'
    matches = re.findall(pattern, md_content)
    links = []
    for m in matches:
        clean_link = m.split('#')[0].split('?')[0].strip()
        if clean_link:
            links.append(clean_link)
    return links


def verify_relative_links(base_dir, links):
    missing = []
    for link in links:
        target_path = os.path.normpath(os.path.join(base_dir, link))
        if not os.path.exists(target_path):
            missing.append(link)
    return missing


class TestEnigmaServices(unittest.TestCase):
    def test_buy_now_relative_links_resolve(self):
        possible_paths = ['BUY_NOW.md', os.path.join('docs', 'BUY_NOW.md')]
        buy_now_path = next((p for p in possible_paths if os.path.exists(p)), None)
        
        if buy_now_path:
            with open(buy_now_path, 'r', encoding='utf-8') as f:
                content = f.read()
            base_dir = os.path.dirname(buy_now_path) or '.'
            links = extract_relative_links(content)
            missing_links = verify_relative_links(base_dir, links)
            self.assertEqual(missing_links, [], f"Missing target files for relative links: {missing_links}")

    def test_missing_target_link_verification_fixture(self):
        # Fixture verifying that missing relative link targets are correctly detected
        sample_md = "[Missing Proof](./non_existent_proof_fixture_spec_test.md)"
        links = extract_relative_links(sample_md)
        missing = verify_relative_links('.', links)
        self.assertIn('./non_existent_proof_fixture_spec_test.md', missing)


if __name__ == '__main__':
    unittest.main()
