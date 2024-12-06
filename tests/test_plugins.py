"""
Tests for the plugin system.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

from src.systems.plugins import (
    Plugin,
    PluginInfo,
    PluginManager,
    PluginEvent,
    PluginLoadEvent,
    PluginEnableEvent,
    PluginDisableEvent
)

@pytest.fixture
def plugin_info():
    return PluginInfo(
        name="TestPlugin",
        version="1.0.0",
        author="Test Author",
        description="Test plugin",
        dependencies=["dep1", "dep2"]
    )

class TestPlugin(Plugin):
    """Test plugin implementation."""
    
    def __init__(self, plugin_info):
        super().__init__(plugin_info)
        self.load_called = False
        self.enable_called = False
        self.disable_called = False
        
    async def on_load(self):
        self.load_called = True
        
    async def on_enable(self):
        self.enable_called = True
        
    async def on_disable(self):
        self.disable_called = True

@pytest.fixture
def plugin(plugin_info):
    return TestPlugin(plugin_info)

@pytest.fixture
def plugin_manager():
    with patch("src.systems.plugins.event_dispatcher", new=AsyncMock()) as mock_dispatcher:
        manager = PluginManager("test_plugins")
        yield manager

@pytest.mark.asyncio
async def test_plugin_lifecycle(plugin):
    """Test plugin load, enable, disable cycle."""
    assert not plugin.enabled
    assert not plugin.load_called
    assert not plugin.enable_called
    assert not plugin.disable_called
    
    await plugin.on_load()
    assert plugin.load_called
    assert not plugin.enabled
    
    await plugin.enable()
    assert plugin.enabled
    assert plugin.enable_called
    
    await plugin.disable()
    assert not plugin.enabled
    assert plugin.disable_called

@pytest.mark.asyncio
async def test_plugin_manager_load_plugin(plugin_manager, tmp_path):
    """Test loading a single plugin."""
    # Create test plugin file
    plugin_dir = tmp_path / "test_plugin"
    plugin_dir.mkdir()
    plugin_file = plugin_dir / "plugin.py"
    
    plugin_code = '''
from src.systems.plugins import Plugin, PluginInfo

PLUGIN_INFO = PluginInfo(
    name="TestPlugin",
    version="1.0.0",
    author="Test Author",
    description="Test plugin",
    dependencies=[]
)

class Plugin(Plugin):
    async def on_load(self): pass
    async def on_enable(self): pass
    async def on_disable(self): pass
'''
    plugin_file.write_text(plugin_code)
    
    # Test loading plugin
    plugin = await plugin_manager.load_plugin(plugin_file)
    assert plugin is not None
    assert plugin.info.name == "TestPlugin"
    assert "TestPlugin" in plugin_manager.plugins

@pytest.mark.asyncio
async def test_plugin_manager_dependency_order(plugin_manager):
    """Test plugin enable order respects dependencies."""
    # Create mock plugins
    plugins = {
        "plugin1": TestPlugin(PluginInfo("plugin1", "1.0", "author", "desc", [])),
        "plugin2": TestPlugin(PluginInfo("plugin2", "1.0", "author", "desc", ["plugin1"])),
        "plugin3": TestPlugin(PluginInfo("plugin3", "1.0", "author", "desc", ["plugin2"]))
    }
    
    # Add plugins to manager
    plugin_manager.plugins = plugins
    plugin_manager._load_order = ["plugin3", "plugin1", "plugin2"]
    
    # Get enable order
    enable_order = plugin_manager._get_enable_order()
    
    # Verify dependencies come before dependents
    assert enable_order.index("plugin1") < enable_order.index("plugin2")
    assert enable_order.index("plugin2") < enable_order.index("plugin3")

@pytest.mark.asyncio
async def test_plugin_manager_discover_plugins(plugin_manager, tmp_path):
    """Test plugin discovery."""
    # Create test plugin structure
    plugins_root = tmp_path / "plugins"
    plugins_root.mkdir()
    
    plugin1_dir = plugins_root / "plugin1"
    plugin1_dir.mkdir()
    (plugin1_dir / "plugin.py").write_text('''
from src.systems.plugins import Plugin, PluginInfo
PLUGIN_INFO = PluginInfo("Plugin1", "1.0", "author", "desc")
class Plugin(Plugin):
    async def on_load(self): pass
    async def on_enable(self): pass
    async def on_disable(self): pass
''')
    
    plugin2_dir = plugins_root / "plugin2"
    plugin2_dir.mkdir()
    (plugin2_dir / "plugin.py").write_text('''
from src.systems.plugins import Plugin, PluginInfo
PLUGIN_INFO = PluginInfo("Plugin2", "1.0", "author", "desc")
class Plugin(Plugin):
    async def on_load(self): pass
    async def on_enable(self): pass
    async def on_disable(self): pass
''')
    
    # Set plugins directory
    plugin_manager.plugins_dir = plugins_root
    
    # Test discovery
    plugins = plugin_manager.discover_plugins()
    assert len(plugins) == 2
    assert any(p.name == "Plugin1" for p in plugins)
    assert any(p.name == "Plugin2" for p in plugins)

@pytest.mark.asyncio
async def test_plugin_events(plugin_manager, plugin):
    """Test plugin-related events are dispatched."""
    mock_dispatcher = AsyncMock()
    plugin_manager._event_dispatcher = mock_dispatcher
    
    # Test load event
    await plugin_manager.load_plugin(Path("dummy/path"))
    mock_dispatcher.dispatch.assert_any_call(
        pytest.approx(lambda x: isinstance(x, PluginLoadEvent))
    )
    
    # Test enable event
    await plugin_manager.enable_plugin("TestPlugin")
    mock_dispatcher.dispatch.assert_any_call(
        pytest.approx(lambda x: isinstance(x, PluginEnableEvent))
    )
    
    # Test disable event
    await plugin_manager.disable_plugin("TestPlugin")
    mock_dispatcher.dispatch.assert_any_call(
        pytest.approx(lambda x: isinstance(x, PluginDisableEvent))
    ) 