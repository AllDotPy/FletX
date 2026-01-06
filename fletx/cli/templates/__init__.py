"""
Template management system for FletX CLI.
Handles template loading, processing, and generation.
"""

import os
import shutil
import re
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, TemplateNotFound

from fletx.utils import get_logger
from fletx.utils.exceptions import (
    TemplateError, ValidationError
)


class TemplateManager:
    """
    Manages template operations including loading, processing, and generation.
    """
    
    def __init__(self, templates_dir: Optional[Path] = None):
        """
        Initialize the template manager.
        
        Args:
            templates_dir: Path to the templates directory. If None, uses default.
        """

        if templates_dir is None:
            # Default to templates directory relative to this file
            current_dir = Path(__file__).parent
            templates_dir = current_dir.parent / "templates"
        
        self.templates_dir = Path(templates_dir)
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Add custom filters
        self.jinja_env.filters['camel_case'] = self._camel_case
        self.jinja_env.filters['snake_case'] = self._snake_case
        self.jinja_env.filters['pascal_case'] = self._pascal_case
        self.jinja_env.filters['kebab_case'] = self._kebab_case

    @property
    def logger(self):
        return 
    
    def get_available_templates(self) -> List[str]:
        """Get list of available template names."""

        if not self.templates_dir.exists():
            return []
        
        templates = []
        for item in self.templates_dir.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                templates.append(item.name)
        
        return sorted(templates)
    
    def template_exists(self, template_name: str) -> bool:
        """Check if a template exists."""

        template_path = self.templates_dir / template_name
        return template_path.exists() and template_path.is_dir()
    
    def generate_from_template(
        self, 
        template_name: str, 
        target_path: Path, 
        context: Dict[str, Any],
        target_filename: Optional[str] = None,
        overwrite: bool = False
    ) -> None:
        """
        Generate files from a template.
        
        Args:
            template_name: Name of the template to use
            target_path: Path where files should be generated
            context: Variables to use in template rendering
            overwrite: Whether to overwrite existing files
        """

        template_path = self.templates_dir / template_name
        
        if not self.template_exists(template_name):
            raise TemplateError(f"Template '{template_name}' not found")
        
        # Ensure target directory exists
        target_path.mkdir(parents=True, exist_ok=True)
        
        # Add common context variables
        context = self._enhance_context(context)
        
        # Process template directory
        self._process_template_directory(
            template_path, target_path, context, 
            overwrite = overwrite,
            target_filename = target_filename
        )
    
    def _enhance_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Add common context variables."""

        enhanced = context.copy()
        
        # Add timestamp information
        now = datetime.now()
        enhanced.update({
            'timestamp': now.isoformat(),
            'date': now.strftime('%Y-%m-%d'),
            'year': now.strftime('%Y'),
            'author': os.environ.get('USER', 'Developer'),
        })
        
        # Add formatted versions of name if provided
        if 'name' in enhanced:
            name = enhanced['name']
            enhanced.update({
                'name_camel': self._camel_case(name),
                'name_snake': self._snake_case(name),
                'name_pascal': self._pascal_case(name),
                'name_kebab': self._kebab_case(name),
            })
        
        return enhanced
    
    def _process_template_directory(
        self, 
        template_path: Path, 
        target_path: Path, 
        context: Dict[str, Any],
        overwrite: bool,
        target_filename: Optional[str] = None
    ) -> None:
        """Recursively process a template directory."""

        for item in template_path.iterdir():
            if item.name.startswith('.') and not item.name.endswith('.tpl'):
                continue
            
            # Process the item name through template engine
            item_name = (
                self._render_string(item.name, context) 
                if not target_filename 
                else target_filename
            )
            target_item = target_path / item_name 
            
            if item.is_dir():
                # Recursively process subdirectory
                target_item.mkdir(exist_ok=True)
                self._process_template_directory(
                    item, target_item, context, overwrite,
                    target_filename = target_filename
                )
            else:
                # Process file
                self._process_template_file(item, target_item, context, overwrite)
    
    def _process_template_file(
        self, 
        template_file: Path, 
        target_file: Path, 
        context: Dict[str, Any],
        overwrite: bool,
    ) -> None:
        """Process a single template file."""

        # Check if target file exists and overwrite is not allowed
        if target_file.exists() and not overwrite:
            print(f"Skipping existing file: {target_file}")
            return
        
        # Handle different file types
        if template_file.suffix == '.tpl':
            # Template file - render and remove .tpl extension
            if target_file.stem == template_file.stem:
                target_file = target_file.with_suffix('') #_name(target_file.stem)
            
            content = self._render_template_file(template_file, context)
            target_file.write_text(content, encoding='utf-8')
            print(f"Generated: {target_file}")

        else:
            # Regular file - copy as is
            shutil.copy2(template_file, target_file)
            print(f"Copied: {target_file}")
    
    def _render_template_file(
        self, 
        template_file: Path, 
        context: Dict[str, Any]
    ) -> str:
        """Render a template file with context."""

        try:
            # Get relative path from templates directory
            relative_path = template_file.relative_to(self.templates_dir)
            template = self.jinja_env.get_template(str(relative_path).replace(os.sep, '/'))
            return template.render(**context)
        
        # Template not found
        except TemplateNotFound:
            raise TemplateError(
                f"Template file not found: {template_file}"
            )
        
        # Unexpected errors
        except Exception as e:
            raise TemplateError(
                f"Error rendering template {template_file}: {e}"
            )
    
    def _render_string(
        self, 
        template_string: str, 
        context: Dict[str, Any]
    ) -> str:
        """Render a template string with context."""

        try:
            template = self.jinja_env.from_string(template_string)
            return template.render(**context)
        except Exception as e:
            raise TemplateError(
                f"Error rendering template string '{template_string}': {e}"
            )
    
    # String transformation filters
    @staticmethod
    def _camel_case(value: str) -> str:
        """Convert string to camelCase."""

        words = re.findall(r'[a-zA-Z0-9]+', value)
        if not words:
            return value
        return words[0].lower() + ''.join(word.capitalize() for word in words[1:])
    
    @staticmethod
    def _snake_case(value: str) -> str:
        """Convert string to snake_case."""

        # Insert underscores before uppercase letters
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', value)
        # Insert underscores before uppercase letters that follow lowercase letters or numbers
        s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
        # Replace non-alphanumeric characters with underscores
        s3 = re.sub(r'[^a-zA-Z0-9_]', '_', s2)
        # Remove multiple consecutive underscores
        s4 = re.sub(r'_+', '_', s3)
        return s4.lower().strip('_')
    
    @staticmethod
    def _pascal_case(value: str) -> str:
        """Convert string to PascalCase."""

        words = re.findall(r'[a-zA-Z0-9]+', value)
        return ''.join(word.capitalize() for word in words)
    
    @staticmethod
    def _kebab_case(value: str) -> str:
        """Convert string to kebab-case."""
        
        # Insert hyphens before uppercase letters
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1-\2', value)
        # Insert hyphens before uppercase letters that follow lowercase letters or numbers
        s2 = re.sub('([a-z0-9])([A-Z])', r'\1-\2', s1)
        # Replace non-alphanumeric characters with hyphens
        s3 = re.sub(r'[^a-zA-Z0-9-]', '-', s2)
        # Remove multiple consecutive hyphens
        s4 = re.sub(r'-+', '-', s3)
        return s4.lower().strip('-')


class TemplateValidator:
    """
    Validates template names and ensures they follow conventions.
    """
    
    @staticmethod
    def validate_name(name: str, target_type: str = "template") -> None:
        """
        Validate a template name.
        
        Args:
            name: The name to validate
            target_type: Type of template (for error messages)
        """
        if not name:
            raise ValidationError(f"{target_type.capitalize()} name cannot be empty.")
        
        # Check if name contains only valid characters
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', name):
            raise ValidationError(
                f"{target_type.capitalize()} name must start with a letter and contain only "
                "letters, numbers, and underscores."
            )
        
        # Check if name is too long
        if len(name) > 50:
            raise ValidationError(f"{target_type.capitalize()} name is too long (max 50 characters).")
        
        # Check if name is a Python keyword
        import keyword
        if keyword.iskeyword(name):
            raise ValidationError(f"'{name}' is a Python keyword and cannot be used as a {target_type} name.")
        
        # Check if name conflicts with common Python modules
        common_modules = {
            'sys', 'os', 'json', 'time', 'datetime', 'random', 'math', 'collections',
            'functools', 'itertools', 'pathlib', 'typing', 'dataclasses', 'enum',
            'abc', 'contextlib', 'copy', 'pickle', 'sqlite3', 'urllib', 'http',
            'threading', 'multiprocessing', 'asyncio', 'concurrent', 'queue',
            'flet', 'fletx'
        }
        
        if name.lower() in common_modules:
            raise ValidationError(
                f"'{name}' conflicts with a common Python module name. "
                f"Please choose a different {target_type} name."
            )
    
    @staticmethod
    def validate_path(path: str) -> None:
        """Validate a file path."""
        if not path:
            raise ValidationError("Path cannot be empty.")
        
        # Check for invalid characters
        invalid_chars = '<>:"|?*'
        if any(char in path for char in invalid_chars):
            raise ValidationError(f"Path contains invalid characters: {invalid_chars}")
        
        # Check for reserved names on Windows
        reserved_names = {
            'CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4', 'COM5',
            'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2', 'LPT3', 'LPT4',
            'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
        }
        
        path_parts = Path(path).parts
        for part in path_parts:
            if part.upper() in reserved_names:
                raise ValidationError(
                    f"'{part}' is a reserved name and cannot be used in paths."
                )
