"""
Plugin system module for loading and managing game plugins.
"""

import asyncio
import importlib.util
import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Type

from .events import Event, EventDispatcher, event_dispatcher

logger = logging.getLogger(__name__)

@dataclass
class PluginInfo:
    """Plugin metadata and information."""
    name: str
    version: str
    author: str
    description: str
    dependencies: List[str] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []

class Plugin(ABC):
    """Base class for all plugins."""
    
    def __init__(self, plugin_info: PluginInfo):
        self.info = plugin_info
        self._enabled = False
        
    @property
    def enabled(self) -> bool:
        """Whether the plugin is currently enabled."""
        return self._enabled
        
    @abstractmethod
    async def on_load(self) -> None:
        """Called when the plugin is loaded."""
        pass
        
    @abstractmethod
    async def on_enable(self) -> None:
        """Called when the plugin is enabled."""
        pass
        
    @abstractmethod
    async def on_disable(self) -> None:
        """Called when the plugin is disabled."""
        pass
        
    async def enable(self) -> None:
        """Enable the plugin."""
        if not self._enabled:
            await self.on_enable()
            self._enabled = True
            logger.info(f"Enabled plugin: {self.info.name}")
            
    async def disable(self) -> None:
        """Disable the plugin."""
        if self._enabled:
            await self.on_disable()
            self._enabled = False
            logger.info(f"Disabled plugin: {self.info.name}")

class PluginManager:
    """
    Manages loading, enabling, and disabling of plugins.
    Handles plugin dependencies and provides plugin discovery.
    """
    
    def __init__(self, plugins_dir: str = "plugins"):
        self.plugins_dir = Path(plugins_dir)
        self.plugins: Dict[str, Plugin] = {}
        self._load_order: List[str] = []
        
    def discover_plugins(self) -> List[PluginInfo]:
        """
        Discover available plugins in the plugins directory.
        Returns list of plugin info without loading the plugins.
        """
        plugin_infos = []
        
        if not self.plugins_dir.exists():
            logger.warning(f"Plugins directory not found: {self.plugins_dir}")
            return plugin_infos
            
        for plugin_path in self.plugins_dir.glob("**/plugin.py"):
            try:
                # Load the module to get plugin info
                spec = importlib.util.spec_from_file_location(
                    f"plugin_{plugin_path.parent.name}",
                    plugin_path
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                if hasattr(module, "PLUGIN_INFO"):
                    plugin_infos.append(module.PLUGIN_INFO)
                    
            except Exception as e:
                logger.error(f"Error discovering plugin at {plugin_path}: {e}")
                
        return plugin_infos
        
    async def load_plugin(self, plugin_path: Path) -> Optional[Plugin]:
        """Load a single plugin from path."""
        try:
            # Import the plugin module
            spec = importlib.util.spec_from_file_location(
                f"plugin_{plugin_path.parent.name}",
                plugin_path
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            if not hasattr(module, "PLUGIN_INFO"):
                raise ValueError("Plugin missing PLUGIN_INFO")
                
            if not hasattr(module, "Plugin"):
                raise ValueError("Plugin missing Plugin class")
                
            # Create plugin instance
            plugin = module.Plugin(module.PLUGIN_INFO)
            await plugin.on_load()
            
            self.plugins[plugin.info.name] = plugin
            self._load_order.append(plugin.info.name)
            
            logger.info(f"Loaded plugin: {plugin.info.name} v{plugin.info.version}")
            return plugin
            
        except Exception as e:
            logger.error(f"Error loading plugin at {plugin_path}: {e}")
            return None
            
    async def load_all_plugins(self) -> None:
        """Load all plugins from the plugins directory."""
        if not self.plugins_dir.exists():
            logger.warning(f"Plugins directory not found: {self.plugins_dir}")
            return
            
        # First pass: Load all plugins
        for plugin_path in self.plugins_dir.glob("**/plugin.py"):
            await self.load_plugin(plugin_path)
            
        # Second pass: Enable plugins in dependency order
        for plugin_name in self._get_enable_order():
            plugin = self.plugins.get(plugin_name)
            if plugin:
                await plugin.enable()
                
    def _get_enable_order(self) -> List[str]:
        """Get plugin names in dependency-aware enable order."""
        visited: Set[str] = set()
        enable_order: List[str] = []
        
        def visit(name: str):
            if name in visited:
                return
            visited.add(name)
            
            plugin = self.plugins.get(name)
            if not plugin:
                return
                
            # First enable dependencies
            for dep in plugin.info.dependencies:
                visit(dep)
                
            enable_order.append(name)
            
        for name in self._load_order:
            visit(name)
            
        return enable_order
        
    async def enable_plugin(self, name: str) -> bool:
        """Enable a specific plugin by name."""
        plugin = self.plugins.get(name)
        if not plugin:
            logger.warning(f"Plugin not found: {name}")
            return False
            
        await plugin.enable()
        return True
        
    async def disable_plugin(self, name: str) -> bool:
        """Disable a specific plugin by name."""
        plugin = self.plugins.get(name)
        if not plugin:
            logger.warning(f"Plugin not found: {name}")
            return False
            
        await plugin.disable()
        return True
        
    def get_plugin(self, name: str) -> Optional[Plugin]:
        """Get a plugin instance by name."""
        return self.plugins.get(name)

# Global plugin manager instance
plugin_manager = PluginManager()

# Example plugin events
class PluginEvent(Event):
    """Base class for plugin-related events."""
    pass

class PluginLoadEvent(PluginEvent):
    """Fired when a plugin is loaded."""
    def __init__(self, plugin: Plugin):
        super().__init__(name="plugin_load")
        self.plugin = plugin

class PluginEnableEvent(PluginEvent):
    """Fired when a plugin is enabled."""
    def __init__(self, plugin: Plugin):
        super().__init__(name="plugin_enable")
        self.plugin = plugin

class PluginDisableEvent(PluginEvent):
    """Fired when a plugin is disabled."""
    def __init__(self, plugin: Plugin):
        super().__init__(name="plugin_disable")
        self.plugin = plugin 