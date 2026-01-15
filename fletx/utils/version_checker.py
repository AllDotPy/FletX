"""
Version compatibility checker for FletX and Flet packages.
"""

import sys
import subprocess
from typing import Optional, Tuple, Dict, List
from packaging import version
from packaging.specifiers import SpecifierSet


class VersionInfo:
    """Container for version information."""
    
    def __init__(self, version_str: str, package_name: str):
        self.version_str = version_str
        self.package_name = package_name
        self.version = version.parse(version_str)
    
    def __str__(self) -> str:
        return f"{self.package_name} v{self.version_str}"
    
    def __repr__(self) -> str:
        return f"VersionInfo({self.package_name}, {self.version_str})"


class CompatibilityResult:
    """Result of compatibility check."""
    
    def __init__(self, is_compatible: bool, fletx_version: VersionInfo, 
                 flet_version: VersionInfo, message: str = "", 
                 suggestions: List[str] = None):
        self.is_compatible = is_compatible
        self.fletx_version = fletx_version
        self.flet_version = flet_version
        self.message = message
        self.suggestions = suggestions or []
    
    def __str__(self) -> str:
        status = "✅" if self.is_compatible else "❌"
        return f"{status} {self.fletx_version} is {'compatible' if self.is_compatible else 'incompatible'} with {self.flet_version}"


class VersionChecker:
    """Version compatibility checker for FletX and Flet."""
    
    # Compatibility matrix: FletX version -> supported Flet versions
    COMPATIBILITY_MATRIX = {
        "0.1.4": {
            "flet": ">=0.28.3,<0.30.0",
            "python": ">=3.12,<3.14"
        },
        "0.1.3": {
            "flet": ">=0.27.0,<0.29.0",
            "python": ">=3.12,<3.14"
        },
        "0.1.2": {
            "flet": ">=0.26.0,<0.28.0",
            "python": ">=3.11,<3.14"
        },
        "0.1.1": {
            "flet": ">=0.25.0,<0.27.0",
            "python": ">=3.11,<3.14"
        },
        "0.1.0": {
            "flet": ">=0.24.0,<0.26.0",
            "python": ">=3.11,<3.14"
        }
    }
    
    def __init__(self):
        self._fletx_version: Optional[VersionInfo] = None
        self._flet_version: Optional[VersionInfo] = None
        self._python_version: Optional[VersionInfo] = None
    
    def get_fletx_version(self) -> VersionInfo:
        """Get the current FletX version."""
        if self._fletx_version is None:
            try:
                from fletx import __version__
                self._fletx_version = VersionInfo(__version__, "FletX")
            except ImportError:
                # Try to get version from package metadata
                version_str = self._get_package_version("fletx")
                self._fletx_version = VersionInfo(version_str, "FletX")
        
        return self._fletx_version
    
    def get_flet_version(self) -> VersionInfo:
        """Get the current Flet version."""
        if self._flet_version is None:
            version_str = self._get_package_version("flet")
            self._flet_version = VersionInfo(version_str, "Flet")
        
        return self._flet_version
    
    def get_python_version(self) -> VersionInfo:
        """Get the current Python version."""
        if self._python_version is None:
            version_str = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
            self._python_version = VersionInfo(version_str, "Python")
        
        return self._python_version
    
    def _get_package_version(self, package_name: str) -> str:
        """Get package version using pip show."""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "show", package_name],
                capture_output=True,
                text=True,
                check=True
            )
            
            for line in result.stdout.split('\n'):
                if line.startswith('Version:'):
                    return line.split(':', 1)[1].strip()
            
            raise ValueError(f"Version not found for {package_name}")
            
        except (subprocess.CalledProcessError, ValueError) as e:
            raise ImportError(f"Could not determine version for {package_name}: {e}")
    
    def check_compatibility(self) -> CompatibilityResult:
        """Check compatibility between FletX and Flet versions."""
        try:
            fletx_version = self.get_fletx_version()
            flet_version = self.get_flet_version()
            python_version = self.get_python_version()
            
            # Get compatibility requirements for FletX version
            requirements = self._get_compatibility_requirements(fletx_version.version_str)
            
            if not requirements:
                return CompatibilityResult(
                    is_compatible=False,
                    fletx_version=fletx_version,
                    flet_version=flet_version,
                    message=f"Unknown FletX version {fletx_version.version_str}",
                    suggestions=["Please check the documentation for supported versions"]
                )
            
            # Check Flet version compatibility
            flet_spec = SpecifierSet(requirements["flet"])
            flet_compatible = flet_version.version in flet_spec
            
            # Check Python version compatibility
            python_spec = SpecifierSet(requirements["python"])
            python_compatible = python_version.version in python_spec
            
            is_compatible = flet_compatible and python_compatible
            
            # Generate messages and suggestions
            message, suggestions = self._generate_compatibility_message(
                fletx_version, flet_version, python_version,
                flet_compatible, python_compatible, requirements
            )
            
            return CompatibilityResult(
                is_compatible=is_compatible,
                fletx_version=fletx_version,
                flet_version=flet_version,
                message=message,
                suggestions=suggestions
            )
            
        except Exception as e:
            return CompatibilityResult(
                is_compatible=False,
                fletx_version=VersionInfo("unknown", "FletX"),
                flet_version=VersionInfo("unknown", "Flet"),
                message=f"Error checking compatibility: {e}",
                suggestions=["Please ensure both FletX and Flet are properly installed"]
            )
    
    def _get_compatibility_requirements(self, fletx_version_str: str) -> Optional[Dict[str, str]]:
        """Get compatibility requirements for a FletX version."""
        # Normalize version string (remove pre-release identifiers for matrix lookup)
        normalized_version = self._normalize_version_for_matrix(fletx_version_str)  # noqa: F841
        
        # Find the best matching requirements
        for matrix_version, requirements in self.COMPATIBILITY_MATRIX.items():
            if self._version_matches(fletx_version_str, matrix_version):
                return requirements
        
        return None
    
    def _normalize_version_for_matrix(self, version_str: str) -> str:
        """Normalize version string for matrix lookup."""
        # Remove pre-release identifiers (e.g., "0.1.4.b1" -> "0.1.4")
        parsed = version.parse(version_str)
        return f"{parsed.major}.{parsed.minor}.{parsed.micro}"
    
    def _version_matches(self, version_str: str, matrix_version: str) -> bool:
        """Check if version matches matrix version."""
        try:
            parsed_version = version.parse(version_str)
            parsed_matrix = version.parse(matrix_version)
            
            # Check if major and minor versions match
            return (parsed_version.major == parsed_matrix.major and 
                    parsed_version.minor == parsed_matrix.minor)
        except:  # noqa: E722
            return False
    
    def _generate_compatibility_message(
        self, fletx_version: VersionInfo, flet_version: VersionInfo, 
        python_version: VersionInfo, flet_compatible: bool, 
        python_compatible: bool, requirements: Dict[str, str]
    ) -> Tuple[str, List[str]]:
        """Generate compatibility message and suggestions."""
        messages = []
        suggestions = []
        
        if flet_compatible and python_compatible:
            messages.append(f"FletX {fletx_version.version_str} is compatible with Flet {flet_version.version_str}")
        else:
            if not flet_compatible:
                messages.append(f"Flet {flet_version.version_str} is not compatible with FletX {fletx_version.version_str}")
                suggestions.append(f"Please upgrade/downgrade Flet to a version compatible with {requirements['flet']}")
            
            if not python_compatible:
                messages.append(f"Python {python_version.version_str} is not compatible with FletX {fletx_version.version_str}")
                suggestions.append(f"Please use Python version compatible with {requirements['python']}")
        
        # Add general suggestions
        if not flet_compatible:
            suggestions.extend([
                "Check the FletX documentation for the latest compatibility information",
                "Consider updating FletX to the latest version if available"
            ])
        
        return " ".join(messages), suggestions
