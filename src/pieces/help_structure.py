"""
Modular help structure for CLI commands.
Provides a clean, structured way to define help examples with sections, headers, and commands.
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class HelpExample:
    """A single help example with command and description."""

    command: str
    description: Optional[str] = None


@dataclass
class HelpSection:
    """A section of help examples with a header and command template."""

    header: str
    command_template: Optional[str] = None
    note: Optional[str] = None
    description: Optional[str] = None
    examples: List[HelpExample] = field(default_factory=list)


@dataclass
class CommandHelp:
    """Complete help structure for a command."""

    sections: List[HelpSection] = field(default_factory=list)

    def add_section(self, section: HelpSection) -> "CommandHelp":
        """Add a section to the help structure."""
        self.sections.append(section)
        return self

    def create_section(
        self,
        header: str,
        command_template: Optional[str] = None,
        description: Optional[str] = None,
        note: Optional[str] = None,
    ) -> HelpSection:
        """Create and add a new section."""
        section = HelpSection(
            header=header,
            command_template=command_template,
            description=description,
            note=note,
        )
        self.add_section(section)
        return section


class HelpBuilder:
    """Builder class for creating structured help content."""

    def __init__(self):
        self.help = CommandHelp()

    def section(
        self,
        header: str,
        command_template: Optional[str] = None,
        description: Optional[str] = None,
        note: Optional[str] = None,
    ) -> "SectionBuilder":
        """Start building a new section."""
        section = self.help.create_section(
            header, command_template, description, note=note
        )
        return SectionBuilder(section, self)

    def build(self) -> CommandHelp:
        """Build and return the final help structure."""
        return self.help


class SectionBuilder:
    """Builder for help sections."""

    def __init__(self, section: HelpSection, parent: HelpBuilder):
        self.sections = section
        self.parent = parent

    def example(
        self, command: str, description: Optional[str] = None
    ) -> "SectionBuilder":
        """Add an example to this section."""
        self.sections.examples.append(HelpExample(command, description))
        return self

    def section(
        self,
        header: str,
        command_template: Optional[str] = None,
        description: Optional[str] = None,
        note: Optional[str] = None,
    ) -> "SectionBuilder":
        """Start building a new section."""
        return self.parent.section(header, command_template, description, note)

    def build(self) -> CommandHelp:
        """Build and return the final help structure."""
        return self.parent.build()
