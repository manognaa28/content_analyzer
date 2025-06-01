import json
import textstat
import re
from typing import Dict, List, Optional
from bs4 import BeautifulSoup
from nltk.tokenize import sent_tokenize
from nltk import download
from nltk.sentiment import SentimentIntensityAnalyzer
from config import AppConfig

class ContentAnalyzer:
    """Analyzer for evaluating documentation content quality."""
    
    def __init__(self):
        self.api_key = AppConfig.get_api_key()
        self.sia = SentimentIntensityAnalyzer()
        download('punkt')  # Download NLTK tokenizer
        
    def analyze_readability(self, content: str) -> Dict:
        """Analyze content readability for marketers."""
        analysis = {
            'flesch_kincaid_grade': textstat.flesch_kincaid_grade(content),
            'gunning_fog': textstat.gunning_fog(content),
            'sentences': sent_tokenize(content),
            'sentiment': self.sia.polarity_scores(content)
        }
        
        # Calculate average sentence length
        sentences = analysis['sentences']
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
        
        # Analyze technical terms
        technical_terms = len(re.findall(r'\b(?:API|SDK|Integration|Analytics|Metrics|Segmentation|Campaign|Automation|Trigger|Event)\b', content, re.IGNORECASE))
        
        # Determine readability score
        fk_grade = analysis['flesch_kincaid_grade']
        readability_score = 100 - (fk_grade * 10)
        
        assessment = {
            'score': readability_score,
            'grade_level': fk_grade,
            'technical_terms': technical_terms,
            'avg_sentence_length': avg_sentence_length,
            'sentiment': analysis['sentiment']['compound'],
            'recommendations': []
        }
        
        # Generate recommendations based on analysis
        if fk_grade > 12:
            assessment['recommendations'].append(
                "Simplify complex sentences and reduce technical jargon for better marketer understanding"
            )
        
        if avg_sentence_length > 25:
            assessment['recommendations'].append(
                "Break down long sentences into shorter, more digestible chunks"
            )
        
        if technical_terms > len(sentences) * 0.2:  # More than 20% technical terms
            assessment['recommendations'].append(
                "Add more business-focused explanations alongside technical terms"
            )
        
        return assessment
    
    def analyze_structure(self, content: str) -> Dict:
        """Analyze content structure and flow."""
        # Split content into sections using common heading patterns
        sections = re.split(r'\n\n+|\n\s*[-=]+\s*\n', content)
        
        # Count headings and paragraphs
        headings = []
        paragraphs = []
        lists = 0
        
        for section in sections:
            section = section.strip()
            if not section:
                continue
                
            # Check if this is a heading
            if re.match(r'^[A-Z][^\n]*$', section) or \
               re.match(r'^\d+\.\s+', section) or \
               re.match(r'^[A-Za-z0-9]+\.', section):
                headings.append(section)
            else:
                # Count bullet points in paragraphs
                bullet_points = re.findall(r'\n\s*[•-]\s+', section)
                lists += len(bullet_points)
                paragraphs.append(section)
                
        # Analyze paragraph length
        long_paragraphs = [p for p in paragraphs if len(p.split()) > 100]
        
        assessment = {
            'headings': len(headings),
            'lists': lists,
            'paragraphs': len(paragraphs),
            'long_paragraphs': len(long_paragraphs),
            'recommendations': []
        }
        
        # Generate recommendations
        if len(headings) < 3:
            assessment['recommendations'].append(
                "Add more descriptive headings to improve content organization"
            )
        
        if len(long_paragraphs) > 0:
            assessment['recommendations'].append(
                f"Break down {len(long_paragraphs)} long paragraphs into shorter, more focused sections"
            )
        
        if lists < len(paragraphs) * 0.2:
            assessment['recommendations'].append(
                "Use more bullet points or numbered lists to highlight key points"
            )
        
        return assessment
    
    def analyze_completeness(self, content: str) -> Dict:
        """Analyze content completeness and examples."""
        examples = len(re.findall(r'\b(?:Example|For example|To illustrate|Consider this example)\b', content, re.IGNORECASE))
        steps = len(re.findall(r'\b(?:Step \d+|1\.|2\.|3\.)\b', content))
        
        # Check for common sections
        sections = {
            'prerequisites': 'prerequisites' in content.lower(),
            'setup': 'setup' in content.lower(),
            'configuration': 'configuration' in content.lower(),
            'troubleshooting': 'troubleshooting' in content.lower()
        }
        
        assessment = {
            'examples': examples,
            'steps': steps,
            'sections': sections,
            'recommendations': []
        }
        
        # Generate recommendations
        if examples < 2:
            assessment['recommendations'].append(
                "Add more practical examples to illustrate concepts"
            )
        
        if steps < 3:
            assessment['recommendations'].append(
                "Break down complex procedures into clear, numbered steps"
            )
        
        missing_sections = [k for k, v in sections.items() if not v]
        if missing_sections:
            assessment['recommendations'].append(
                f"Add sections for: {', '.join(missing_sections)}"
            )
        
        return assessment
    
    def analyze_style(self, content: str) -> Dict:
        """Analyze content style against Microsoft Style Guide principles."""
        sentences = sent_tokenize(content)
        
        # Analyze voice and tone
        passive_voice = len(re.findall(r'\b(?:is|are|was|were|be|being|been)\b', content))
        second_person = len(re.findall(r'\b(you|your)\b', content, re.IGNORECASE))
        
        # Check for complex sentences
        complex_sentences = [s for s in sentences if len(s.split()) > 25]
        
        # Look for jargon
        jargon = len(re.findall(r'\b(?:API|SDK|Integration|Analytics|Metrics|Segmentation|Campaign|Automation|Trigger|Event)\b', content, re.IGNORECASE))
        
        assessment = {
            'passive_voice': passive_voice,
            'second_person': second_person,
            'complex_sentences': len(complex_sentences),
            'jargon': jargon,
            'recommendations': []
        }
        
        # Generate recommendations
        if passive_voice > len(sentences) * 0.2:
            assessment['recommendations'].append(
                "Reduce passive voice usage to make content more engaging"
            )
        
        if second_person < len(sentences) * 0.3:
            assessment['recommendations'].append(
                "Use more second-person voice (you/your) to make content more personal"
            )
        
        if len(complex_sentences) > len(sentences) * 0.2:
            assessment['recommendations'].append(
                "Simplify complex sentences for better readability"
            )
        
        if jargon > len(sentences) * 0.2:
            assessment['recommendations'].append(
                "Reduce technical jargon and provide clear explanations"
            )
        
        return assessment
    
    def analyze_content(self, url: str, content: str) -> Dict:
        """Perform comprehensive content analysis."""
        analysis = {
            'url': url,
            'readability': self.analyze_readability(content),
            'structure': self.analyze_structure(content),
            'completeness': self.analyze_completeness(content),
            'style': self.analyze_style(content)
        }
        
        return analysis

def analyze_processed_content(input_file: str, output_file: str) -> None:
    """Analyze processed content from JSON file."""
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    analyzer = ContentAnalyzer()
    results = []
    
    for item in data:
        if item['status'] == 'success':
            analysis = analyzer.analyze_content(item['url'], item['content'])
            results.append(analysis)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    input_file = 'output/processed_content.json'
    output_file = 'output/content_analysis.json'
    analyze_processed_content(input_file, output_file)
