import xml.etree.ElementTree as ET
from xml.dom import minidom
from typing import List, Dict, Any
import os
from config import XML_DIR
from scraper.utils import setup_logger

logger = setup_logger(__name__)

def _prettify_xml(elem: ET.Element) -> str:
    """Return a pretty-printed XML string for the Element."""
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

def export_contests_to_xml(contests: List[Dict[str, Any]], filename: str = "contests.xml"):
    """
    Exports a list of contests to an XML file.
    """
    try:
        root = ET.Element("contests")
        
        for c in contests:
            contest_elem = ET.SubElement(root, "contest")
            
            ET.SubElement(contest_elem, "contest_id").text = str(c.get("contest_id", ""))
            ET.SubElement(contest_elem, "name").text = str(c.get("contest_name", ""))
            ET.SubElement(contest_elem, "start_time").text = str(c.get("start_time", ""))
            ET.SubElement(contest_elem, "duration").text = str(c.get("duration", ""))
            ET.SubElement(contest_elem, "rated_range").text = str(c.get("rated_range", ""))
            ET.SubElement(contest_elem, "url").text = str(c.get("url", ""))
            
        xml_str = _prettify_xml(root)
        
        filepath = os.path.join(XML_DIR, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(xml_str)
            
        logger.info(f"Exported {len(contests)} contests to {filepath}")
    except Exception as e:
        logger.error(f"Error exporting contests to XML: {e}")

def export_problems_to_xml(problems: List[Dict[str, Any]], filename: str = "problems.xml"):
    """
    Exports a list of problems to an XML file.
    """
    try:
        root = ET.Element("problems")
        
        for p in problems:
            problem_elem = ET.SubElement(root, "problem")
            
            ET.SubElement(problem_elem, "problem_id").text = str(p.get("problem_id", ""))
            ET.SubElement(problem_elem, "contest_id").text = str(p.get("contest_id", ""))
            ET.SubElement(problem_elem, "title").text = str(p.get("title", ""))
            ET.SubElement(problem_elem, "difficulty").text = str(p.get("difficulty", "")) if p.get("difficulty") else ""
            ET.SubElement(problem_elem, "time_limit").text = str(p.get("time_limit", "")) if p.get("time_limit") else ""
            ET.SubElement(problem_elem, "memory_limit").text = str(p.get("memory_limit", "")) if p.get("memory_limit") else ""
            ET.SubElement(problem_elem, "url").text = str(p.get("url", ""))
            
        xml_str = _prettify_xml(root)
        
        filepath = os.path.join(XML_DIR, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(xml_str)
            
        logger.info(f"Exported {len(problems)} problems to {filepath}")
    except Exception as e:
        logger.error(f"Error exporting problems to XML: {e}")
