"""
Command to generate FletX components (controllers, views, services, etc.).
"""

from pathlib import Path
from typing import Optional

from fletx.cli.commands import TemplateCommand, CommandParser
from fletx.utils.exceptions import CommandExecutionError
from fletx.cli.templates import TemplateManager


class ComponentCommand(TemplateCommand):
    """Generate FletX components like controllers, views, and services."""
    
    command_name = "generate"
    target_tpl_name = "Component"
    
    def add_arguments(self, parser: CommandParser) -> None:
        """Add arguments specific to the component command."""
        parser.add_argument(
            "type",
            choices=["controller", "service", "model", "component", "page", "middleware", "guard"],
            help="Type of component to generate"
        )
        parser.add_argument(
            "name",
            help="Name of the component"
        )
        parser.add_argument(
            "--output-dir",
            help="Directory where the component should be created (default: based on type)"
        )
        parser.add_argument(
            "--template",
            help="Specific template to use (default: based on component type)"
        )
        parser.add_argument(
            "--overwrite",
            action="store_true",
            help="Overwrite existing files if they exist"
        )
        parser.add_argument(
            "--with-test",
            action="store_true",
            help="Generate test file for the component"
        )
        parser.add_argument(
            "--binding",
            help="Create binding for the component (e.g., user, product)"
        )
    
    def handle(self, **kwargs) -> None:
        """Handle the component command."""

        component_type = kwargs.get("type")
        name = kwargs.get("name")
        output_dir = kwargs.get("output_dir")
        template = kwargs.get("template")
        overwrite = kwargs.get("overwrite", False)
        with_test = kwargs.get("with_test", False)
        binding = kwargs.get("binding")
        
        # Validate component name
        self.validate_name(name)
        
        # Determine template name
        if not template:
            template = self._get_default_template(component_type)
        
        # Determine output directory
        if not output_dir:
            output_dir = self._get_default_output_dir(component_type)
        
        target_dir = Path(output_dir)
        
        # Initialize template manager
        template_manager = TemplateManager()
        
        # Check if template exists
        if not template_manager.template_exists(template):
            available_templates = template_manager.get_available_templates()
            raise CommandExecutionError(
                f"Template '{template}' not found. "
                f"Available templates: {', '.join(available_templates)}"
            )
        
        # Prepare context for template rendering
        context = {
            "name": name,
            "component_type": component_type,
            "binding": binding,
            "with_test": with_test,
        }
        
        try:
            # Generate component from template
            print(f"Generating {component_type} '{name}'...")
            template_manager.generate_from_template(
                template, target_dir, context, 
                overwrite = overwrite,
                target_filename = f'{name}_{component_type}.py'.lower()
            )
            
            # Generate test file if requested
            if with_test:
                self._generate_test_file(
                    component_type, 
                    name, 
                    target_dir, 
                    context, 
                    overwrite
                )
            
            # Generate binding if specified
            if binding:
                self._generate_binding(
                    component_type, 
                    name, 
                    binding, 
                    target_dir, 
                    context, 
                    overwrite
                )
            
            print(f"\n{component_type.capitalize()} '{name}' generated successfully!")
            self._print_usage_instructions(component_type, name, target_dir)
            
        except Exception as e:
            raise CommandExecutionError(
                f"Failed to generate component: {e}"
            )
    
    def _get_default_template(self, component_type: str) -> str:
        """Get the default template for a component type."""

        template_mapping = {
            "controller": "controller",
            "service": "service",
            "model": "model",
            "component": "component",
            "page": "page",
            "middleware": "middleware",
            "guard": "guard"
        }
        
        return template_mapping.get(component_type, "component")
    
    def _get_default_output_dir(self, component_type: str) -> str:
        """Get the default output directory for a component type."""

        # Follow FletX convention structure
        dir_mapping = {
            "controller": "app/controllers",
            "service": "app/services", 
            "model": "app/models",
            "component": "app/components",
            "page": "app/pages",
            "middleware": "app/middlewares",
            "guard": "app/guards"
        }
        
        return dir_mapping.get(component_type, "app/components")
    
    def _generate_test_file(
        self, 
        component_type: str, 
        name: str, 
        target_dir: Path, 
        context: dict, 
        overwrite: bool
    ) -> None:
        """Generate a test file for the component."""

        test_template = f"{component_type}_test"
        test_dir = Path("tests") / component_type.lower()
        
        template_manager = TemplateManager()
        
        # Check if test template exists
        if not template_manager.template_exists(test_template):
            print(
                f"Warning: Test template '{test_template}' "
                "not found, skipping test generation."
            )
            return
        
        print(f"Generating test file for {component_type} '{name}'...")
        template_manager.generate_from_template(
            test_template, test_dir, context, overwrite
        )
    
    def _generate_binding(
        self, 
        component_type: str, 
        name: str, 
        binding: str,
        target_dir: Path, 
        context: dict, 
        overwrite: bool
    ) -> None:
        """Generate binding for the component."""

        binding_template = f"{component_type}_binding"
        binding_dir = Path("app/bindings")
        
        template_manager = TemplateManager()
        
        # Check if binding template exists
        if not template_manager.template_exists(binding_template):
            print(
                f"Warning: Binding template '{binding_template}' "
                "not found, skipping binding generation."
            )
            return
        
        binding_context = context.copy()
        binding_context["binding"] = binding
        
        print(
            f"Generating binding for {component_type} "
            f"'{name}' with '{binding}'..."
        )
        template_manager.generate_from_template(
            binding_template, binding_dir, binding_context, overwrite
        )
    
    def _print_usage_instructions(
        self, 
        component_type: str, 
        name: str, 
        target_dir: Path
    ) -> None:
        """Print usage instructions for the generated component."""

        print(f"\n{'='*50}")
        print(f"📦 {component_type.capitalize()} '{name}' created!")
        print(f"{'='*50}")
        
        # Component-specific instructions
        instructions = {
            "controller": [
                f"1. Your controller is located at: {target_dir}/{name.lower()}_controller.py",
                f"2. Add your business logic in the {name}Controller class",
                f"3. Use dependency injection to access services",
                f"4. Register the controller in your bindings if needed"
            ],
            "service": [
                f"1. Your service is located at: {target_dir}/{name.lower()}_service.py",
                f"2. Implement your business logic in the {name}Service class",
                f"3. Register the service in your bindings",
                f"4. Inject the service into controllers that need it"
            ],
            "model": [
                f"1. Your model is located at: {target_dir}/{name.lower()}_model.py",
                f"2. Define your data structure in the {name}Model class",
                f"3. Add validation and serialization methods as needed",
                f"4. Use the model in your controllers and services"
            ],
            "component": [
                f"1. Your widget is located at: {target_dir}/{name.lower()}_component.py",
                f"2. Implement your custom widget in the {name}Widget class",
                f"3. Use the widget in your views and pages",
                f"4. Make it reusable by parameterizing it properly"
            ],
            "page": [
                f"1. Your page is located at: {target_dir}/{name.lower()}_page.py",
                f"2. Define your page layout in the {name}Page class",
                f"3. Add the page to your route configuration",
                f"4. Connect to controllers for business logic"
            ]
        }
        
        component_instructions = instructions.get(component_type, [
            f"1. Your component is located at: {target_dir}",
            f"2. Customize the {name} class as needed",
            f"3. Follow FletX patterns and conventions"
        ])
        
        for instruction in component_instructions:
            print(f"  {instruction}")
        
        print(f"\nNext steps:")
        print(f"  • Edit the generated files to implement your logic")
        print(f"  • Run your application with: fletx run")
        print(f"  • Check the documentation for best practices")
    
    def get_missing_args_message(self) -> str:
        """Get the missing arguments message."""

        return (
            "You must specify a component type and name. "
            "Usage: fletx component <type> <name>"
        )
