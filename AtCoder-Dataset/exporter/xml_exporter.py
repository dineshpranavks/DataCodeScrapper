import sys
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
from pathlib import Path
from typing import List, Optional

# Allow importing from parent directory
sys.path.append(str(Path(__file__).resolve().parent.parent))

from models import Problem
from database.database import Database

class XMLExporter:
    """
    Exports Problem dataclasses to formatted XML files.
    """

    def __init__(self, output_directory: str = "dataset/xml"):
        self.output_dir = Path(output_directory)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _add_element(self, parent: ET.Element, tag: str, text: Optional[str]) -> ET.Element:
        """Helper to create an XML sub-element with text."""
        elem = ET.SubElement(parent, tag)
        elem.text = text if text is not None else ""
        return elem

    def export_problem(self, problem: Problem) -> Optional[Path]:
        """
        Exports a single Problem to an XML file.
        Returns the path to the generated XML file, or None if failed.
        """
        try:
            root = ET.Element("problem")

            self._add_element(root, "problem_id", problem.problem_id)
            self._add_element(root, "contest_id", problem.contest_id)
            self._add_element(root, "title", problem.title)
            self._add_element(root, "problem_url", problem.problem_url)
            self._add_element(root, "statement", problem.statement)
            self._add_element(root, "constraints", problem.constraints)
            self._add_element(root, "input_format", problem.input_format)
            self._add_element(root, "output_format", problem.output_format)
            self._add_element(root, "time_limit", problem.time_limit)
            self._add_element(root, "memory_limit", problem.memory_limit)

            samples_elem = ET.SubElement(root, "samples")
            
            num_samples = max(len(problem.sample_inputs), len(problem.sample_outputs))
            for i in range(num_samples):
                sample_elem = ET.SubElement(samples_elem, "sample", index=str(i + 1))
                
                input_val = problem.sample_inputs[i] if i < len(problem.sample_inputs) else ""
                output_val = problem.sample_outputs[i] if i < len(problem.sample_outputs) else ""
                
                self._add_element(sample_elem, "input", input_val)
                self._add_element(sample_elem, "output", output_val)

            classification = ET.SubElement(root, "classification")
            self._add_element(classification, "topic", problem.topic)
            self._add_element(classification, "subtopic", problem.subtopic)
            self._add_element(classification, "difficulty", problem.difficulty)
            self._add_element(classification, "rating", str(problem.rating) if problem.rating is not None else "")

            # Pretty print using minidom
            xml_str = ET.tostring(root, encoding="utf-8")
            parsed_xml = minidom.parseString(xml_str)
            
            # The encoding parameter ensures the XML declaration is included
            pretty_xml = parsed_xml.toprettyxml(indent="    ", encoding="UTF-8")

            # Clean filename
            safe_filename = "".join(c for c in problem.problem_id if c.isalnum() or c in ('-', '_'))
            if not safe_filename:
                safe_filename = "unknown_problem"
                
            file_path = self.output_dir / f"{safe_filename}.xml"

            with open(file_path, "wb") as f:
                f.write(pretty_xml)

            return file_path

        except Exception as e:
            print(f"Error exporting problem {problem.problem_id}: {e}")
            return None

    def export_all(self, problems: List[Problem]) -> List[Path]:
        """
        Exports a list of Problem objects to XML files.
        """
        exported_paths = []
        for problem in problems:
            print(f"Exporting {problem.problem_id}.xml")
            path = self.export_problem(problem)
            if path:
                exported_paths.append(path)
        
        print("Export Complete")
        print(f"{len(exported_paths)} XML files generated")
        return exported_paths

    def export_from_database(self, database: Database):
        """
        Reads all problems from the database and exports them to XML.
        """
        problems = database.get_all_problems()
        self.export_all(problems)

if __name__ == "__main__":
    db = Database()
    exporter = XMLExporter()
    exporter.export_from_database(db)
