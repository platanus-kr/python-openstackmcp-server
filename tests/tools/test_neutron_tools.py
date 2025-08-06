import pytest
from unittest.mock import Mock
from openstack import exceptions
from openstack_mcp_server.tools.response.neutron import Network
from openstack_mcp_server.tools.neutron_tools import NeutronTools


class TestNeutronTools:
    """Test cases for NeutronTools class."""

    def get_neutron_tools(self) -> NeutronTools:
        """Get an instance of NeutronTools."""
        return NeutronTools()

    def test_get_neutron_networks_success(self, mock_openstack_connect_neutron):
        """Test getting neutron networks successfully."""
        mock_conn = mock_openstack_connect_neutron
        
        # Create mock network objects
        mock_network1 = Mock()
        mock_network1.id = "net-123-abc-def"
        mock_network1.name = "private-network"
        mock_network1.status = "ACTIVE"
        mock_network1.description = "Private network for project"
        mock_network1.admin_state_up = True
        mock_network1.shared = False
        mock_network1.mtu = 1500
        mock_network1.provider_network_type = "vxlan"
        mock_network1.provider_physical_network = None
        mock_network1.provider_segmentation_id = 100
        mock_network1.project_id = "proj-456-ghi-jkl"

        mock_network2 = Mock()
        mock_network2.id = "net-789-mno-pqr"
        mock_network2.name = "public-network"
        mock_network2.status = "ACTIVE"
        mock_network2.description = "Public shared network"
        mock_network2.admin_state_up = True
        mock_network2.shared = True
        mock_network2.mtu = 1450
        mock_network2.provider_network_type = "flat"
        mock_network2.provider_physical_network = "physnet1"
        mock_network2.provider_segmentation_id = None
        mock_network2.project_id = "proj-admin-000"
        
        # Configure mock conn.list_networks()
        mock_conn.list_networks.return_value = [mock_network1, mock_network2]

        # Test get_neutron_networks()
        neutron_tools = self.get_neutron_tools()
        result = neutron_tools.get_neutron_networks()
        
        # Verify results
        expected_network1 = Network(
            id="net-123-abc-def",
            name="private-network",
            status="ACTIVE",
            description="Private network for project",
            is_admin_state_up=True,
            is_shared=False,
            mtu=1500,
            provider_network_type="vxlan",
            provider_physical_network=None,
            provider_segmentation_id=100,
            project_id="proj-456-ghi-jkl"
        )
        
        expected_network2 = Network(
            id="net-789-mno-pqr",
            name="public-network",
            status="ACTIVE",
            description="Public shared network",
            is_admin_state_up=True,
            is_shared=True,
            mtu=1450,
            provider_network_type="flat",
            provider_physical_network="physnet1",
            provider_segmentation_id=None,
            project_id="proj-admin-000"
        )
        
        
        assert len(result) == 2
        assert result[0] == expected_network1
        assert result[1] == expected_network2

        # Verify mock calls
        mock_conn.list_networks.assert_called_once_with(filters={})

    def test_get_neutron_networks_empty_list(self, mock_openstack_connect_neutron):
        """Test getting neutron networks when no networks exist."""
        mock_conn = mock_openstack_connect_neutron
        
        # Empty network list
        mock_conn.list_networks.return_value = []
        
        # Test get_neutron_networks()
        neutron_tools = self.get_neutron_tools()
        result = neutron_tools.get_neutron_networks()
        
        # Verify results
        assert result == []

        # Verify mock calls
        mock_conn.list_networks.assert_called_once_with(filters={})

    def test_get_neutron_networks_with_status_filter(self, mock_openstack_connect_neutron):
        """Test getting neutron networks with status filter."""
        mock_conn = mock_openstack_connect_neutron
        
        # Create mock network objects with different statuses
        mock_network1 = Mock()
        mock_network1.id = "net-active"
        mock_network1.name = "active-network"
        mock_network1.status = "ACTIVE"
        mock_network1.description = None
        mock_network1.admin_state_up = True
        mock_network1.shared = False
        mock_network1.mtu = None
        mock_network1.provider_network_type = None
        mock_network1.provider_physical_network = None
        mock_network1.provider_segmentation_id = None
        mock_network1.project_id = None

        mock_network2 = Mock()
        mock_network2.id = "net-down"
        mock_network2.name = "down-network"
        mock_network2.status = "DOWN"
        mock_network2.description = None
        mock_network2.admin_state_up = False
        mock_network2.shared = False
        mock_network2.mtu = None
        mock_network2.provider_network_type = None
        mock_network2.provider_physical_network = None
        mock_network2.provider_segmentation_id = None
        mock_network2.project_id = None
        
        # Mock should return only the filtered network (server-side filtering)
        mock_conn.list_networks.return_value = [mock_network1]  # Only ACTIVE network

        # Test get_neutron_networks() with status filter
        neutron_tools = self.get_neutron_tools()
        result = neutron_tools.get_neutron_networks(status_filter="ACTIVE")
        
        # Verify only ACTIVE network is returned
        assert len(result) == 1
        assert result[0].id == "net-active"
        assert result[0].status == "ACTIVE"
        
        # Verify mock was called with proper filter
        mock_conn.list_networks.assert_called_once_with(filters={'status': 'ACTIVE'})

    def test_get_neutron_networks_shared_only(self, mock_openstack_connect_neutron):
        """Test getting only shared networks."""
        mock_conn = mock_openstack_connect_neutron
        
        # Create mock network objects
        mock_network1 = Mock()
        mock_network1.id = "net-private"
        mock_network1.name = "private-network"
        mock_network1.status = "ACTIVE"
        mock_network1.description = None
        mock_network1.admin_state_up = True
        mock_network1.shared = False
        mock_network1.mtu = None
        mock_network1.provider_network_type = None
        mock_network1.provider_physical_network = None
        mock_network1.provider_segmentation_id = None
        mock_network1.project_id = None

        mock_network2 = Mock()
        mock_network2.id = "net-shared"
        mock_network2.name = "shared-network"
        mock_network2.status = "ACTIVE"
        mock_network2.description = None
        mock_network2.admin_state_up = True
        mock_network2.shared = True
        mock_network2.mtu = None
        mock_network2.provider_network_type = None
        mock_network2.provider_physical_network = None
        mock_network2.provider_segmentation_id = None
        mock_network2.project_id = None
        
        # Mock should return only the shared network (server-side filtering) 
        mock_conn.list_networks.return_value = [mock_network2]  # Only shared network

        # Test get_neutron_networks() with shared_only filter
        neutron_tools = self.get_neutron_tools()
        result = neutron_tools.get_neutron_networks(shared_only=True)
        
        # Verify only shared network is returned
        assert len(result) == 1
        assert result[0].id == "net-shared"
        assert result[0].is_shared is True
        
        # Verify mock was called with proper filter
        mock_conn.list_networks.assert_called_once_with(filters={'shared': True})

    def test_get_neutron_networks_combined_filters(self, mock_openstack_connect_neutron):
        """Test getting networks with both status and shared filters."""
        mock_conn = mock_openstack_connect_neutron
        
        # Create mock network that matches both filters (ACTIVE and shared)
        mock_network = Mock()
        mock_network.id = "net-active-shared"
        mock_network.name = "active-shared-network"
        mock_network.status = "ACTIVE"
        mock_network.description = None
        mock_network.admin_state_up = True
        mock_network.shared = True
        mock_network.mtu = None
        mock_network.provider_network_type = None
        mock_network.provider_physical_network = None
        mock_network.provider_segmentation_id = None
        mock_network.project_id = None
        
        # Mock should return only the network that matches both filters
        mock_conn.list_networks.return_value = [mock_network]

        # Test get_neutron_networks() with both filters
        neutron_tools = self.get_neutron_tools()
        result = neutron_tools.get_neutron_networks(status_filter="ACTIVE", shared_only=True)
        
        # Verify only the matching network is returned
        assert len(result) == 1
        assert result[0].id == "net-active-shared"
        assert result[0].status == "ACTIVE"
        assert result[0].is_shared is True
        
        # Verify mock was called with both filters
        mock_conn.list_networks.assert_called_once_with(filters={'status': 'ACTIVE', 'shared': True})

    def test_get_neutron_networks_case_insensitive_status(self, mock_openstack_connect_neutron):
        """Test that status filter is case-insensitive (converts to uppercase)."""
        mock_conn = mock_openstack_connect_neutron
        
        # Create mock network
        mock_network = Mock()
        mock_network.id = "net-lowercase-test"
        mock_network.name = "test-network"
        mock_network.status = "ACTIVE"
        mock_network.description = None
        mock_network.admin_state_up = True
        mock_network.shared = False
        mock_network.mtu = None
        mock_network.provider_network_type = None
        mock_network.provider_physical_network = None
        mock_network.provider_segmentation_id = None
        mock_network.project_id = None
        
        mock_conn.list_networks.return_value = [mock_network]

        # Test with lowercase status filter
        neutron_tools = self.get_neutron_tools()
        result = neutron_tools.get_neutron_networks(status_filter="active")
        
        # Verify business logic: lowercase converted to uppercase
        assert len(result) == 1
        assert result[0].status == "ACTIVE"
        
        # Verify mock was called with uppercase filter
        mock_conn.list_networks.assert_called_once_with(filters={'status': 'ACTIVE'})

    def test_get_neutron_networks_empty_string_filter_ignored(self, mock_openstack_connect_neutron):
        """Test that empty string status filter is ignored."""
        mock_conn = mock_openstack_connect_neutron
        
        mock_network = Mock()
        mock_network.id = "net-empty-filter"
        mock_network.name = "test-network"
        mock_network.status = "ACTIVE"
        mock_network.description = None
        mock_network.admin_state_up = True
        mock_network.shared = False
        mock_network.mtu = None
        mock_network.provider_network_type = None
        mock_network.provider_physical_network = None
        mock_network.provider_segmentation_id = None
        mock_network.project_id = None
        
        mock_conn.list_networks.return_value = [mock_network]

        # Test with empty string status filter
        neutron_tools = self.get_neutron_tools()
        result = neutron_tools.get_neutron_networks(status_filter="")
        
        # Verify empty filter was ignored (no status in filters)
        assert len(result) == 1
        mock_conn.list_networks.assert_called_once_with(filters={})

    def test_get_neutron_networks_with_none_status_filter(self, mock_openstack_connect_neutron):
        """Test that None status filter is ignored (same as no filter)."""
        mock_conn = mock_openstack_connect_neutron
        
        mock_network = Mock()
        mock_network.id = "net-none-filter"
        mock_network.name = "test-network"
        mock_network.status = "ACTIVE"
        mock_network.description = None
        mock_network.admin_state_up = True
        mock_network.shared = False
        mock_network.mtu = None
        mock_network.provider_network_type = None
        mock_network.provider_physical_network = None
        mock_network.provider_segmentation_id = None
        mock_network.project_id = None
        
        mock_conn.list_networks.return_value = [mock_network]

        # Test with None status filter (should be ignored)
        neutron_tools = self.get_neutron_tools()
        result = neutron_tools.get_neutron_networks(status_filter=None)
        
        # Verify None filter was ignored (empty filters dict)
        assert len(result) == 1
        mock_conn.list_networks.assert_called_once_with(filters={})

    def test_get_neutron_networks_mixed_case_status_variations(self, mock_openstack_connect_neutron):
        """Test various case combinations for status filter."""
        mock_conn = mock_openstack_connect_neutron
        
        mock_network = Mock()
        mock_network.id = "net-case-test"
        mock_network.name = "case-test-network"
        mock_network.status = "DOWN"
        mock_network.description = None
        mock_network.admin_state_up = False
        mock_network.shared = False
        mock_network.mtu = None
        mock_network.provider_network_type = None
        mock_network.provider_physical_network = None
        mock_network.provider_segmentation_id = None
        mock_network.project_id = None
        
        mock_conn.list_networks.return_value = [mock_network]

        # Test different case variations
        test_cases = ["down", "Down", "DOWN", "dOwN"]
        
        for case_variant in test_cases:
            mock_conn.reset_mock()
            neutron_tools = self.get_neutron_tools()
            result = neutron_tools.get_neutron_networks(status_filter=case_variant)
            
            # All should be converted to uppercase
            mock_conn.list_networks.assert_called_once_with(filters={'status': 'DOWN'})



    def test_create_network_success(self, mock_openstack_connect_neutron):
        """Test creating a network successfully."""
        mock_conn = mock_openstack_connect_neutron
        
        # Create mock network object
        mock_network = Mock()
        mock_network.id = "net-new-123"
        mock_network.name = "new-network"
        mock_network.status = "ACTIVE"
        mock_network.description = "A new network"
        mock_network.admin_state_up = True
        mock_network.shared = False
        mock_network.mtu = 1500
        mock_network.provider_network_type = "vxlan"
        mock_network.provider_physical_network = None
        mock_network.provider_segmentation_id = 200
        mock_network.project_id = "proj-123"

        # Configure mock network.create_network()
        mock_conn.network.create_network.return_value = mock_network

        # Test create_network()
        neutron_tools = self.get_neutron_tools()
        result = neutron_tools.create_network(
            name="new-network",
            description="A new network",
            provider_network_type="vxlan",
            provider_segmentation_id=200
        )
        
        # Verify results
        expected_network = Network(
            id="net-new-123",
            name="new-network",
            status="ACTIVE",
            description="A new network",
            is_admin_state_up=True,
            is_shared=False,
            mtu=1500,
            provider_network_type="vxlan",
            provider_physical_network=None,
            provider_segmentation_id=200,
            project_id="proj-123"
        )
        
        assert result == expected_network

        # Verify mock calls
        expected_args = {
            'name': 'new-network',
            'admin_state_up': True,
            'shared': False,
            'description': 'A new network',
            'provider_network_type': 'vxlan',
            'provider_segmentation_id': 200
        }
        mock_conn.network.create_network.assert_called_once_with(**expected_args)

    def test_create_network_minimal_args(self, mock_openstack_connect_neutron):
        """Test creating a network with minimal arguments."""
        mock_conn = mock_openstack_connect_neutron
        
        # Create mock network object
        mock_network = Mock()
        mock_network.id = "net-minimal-123"
        mock_network.name = "minimal-network"
        mock_network.status = "ACTIVE"
        mock_network.description = None
        mock_network.admin_state_up = True
        mock_network.shared = False
        mock_network.mtu = None
        mock_network.provider_network_type = None
        mock_network.provider_physical_network = None
        mock_network.provider_segmentation_id = None
        mock_network.project_id = None

        mock_conn.network.create_network.return_value = mock_network

        # Test create_network() with minimal args
        neutron_tools = self.get_neutron_tools()
        result = neutron_tools.create_network(name="minimal-network")
        
        # Verify results
        expected_network = Network(
            id="net-minimal-123",
            name="minimal-network",
            status="ACTIVE",
            description=None,
            is_admin_state_up=True,
            is_shared=False,
            mtu=None,
            provider_network_type=None,
            provider_physical_network=None,
            provider_segmentation_id=None,
            project_id=None
        )
        
        assert result == expected_network

        # Verify mock calls
        expected_args = {
            'name': 'minimal-network',
            'admin_state_up': True,
            'shared': False
        }
        mock_conn.network.create_network.assert_called_once_with(**expected_args)



    def test_get_network_detail_success(self, mock_openstack_connect_neutron):
        """Test getting network detail successfully."""
        mock_conn = mock_openstack_connect_neutron
        
        # Create mock network object
        mock_network = Mock()
        mock_network.id = "net-detail-123"
        mock_network.name = "detail-network"
        mock_network.status = "ACTIVE"
        mock_network.description = "Network for detail testing"
        mock_network.admin_state_up = True
        mock_network.shared = True
        mock_network.mtu = 1500
        mock_network.provider_network_type = "vlan"
        mock_network.provider_physical_network = "physnet1"
        mock_network.provider_segmentation_id = 100
        mock_network.project_id = "proj-detail-123"

        # Configure mock network.get_network()
        mock_conn.network.get_network.return_value = mock_network

        # Test get_network_detail()
        neutron_tools = self.get_neutron_tools()
        result = neutron_tools.get_network_detail("net-detail-123")
        
        # Verify results
        expected_network = Network(
            id="net-detail-123",
            name="detail-network",
            status="ACTIVE",
            description="Network for detail testing",
            is_admin_state_up=True,
            is_shared=True,
            mtu=1500,
            provider_network_type="vlan",
            provider_physical_network="physnet1",
            provider_segmentation_id=100,
            project_id="proj-detail-123"
        )
        
        assert result == expected_network

        # Verify mock calls
        mock_conn.network.get_network.assert_called_once_with("net-detail-123")

    def test_get_network_detail_not_found(self, mock_openstack_connect_neutron):
        """Test getting network detail when network not found."""
        mock_conn = mock_openstack_connect_neutron
        
        # Configure mock to return None (network not found)
        mock_conn.network.get_network.return_value = None

        # Test get_network_detail()
        neutron_tools = self.get_neutron_tools()
        
        # Verify exception is raised
        with pytest.raises(Exception, match="Network with ID nonexistent-net not found"):
            neutron_tools.get_network_detail("nonexistent-net")



    def test_update_network_success(self, mock_openstack_connect_neutron):
        """Test updating a network successfully."""
        mock_conn = mock_openstack_connect_neutron
        
        # Create mock updated network object
        mock_network = Mock()
        mock_network.id = "net-update-123"
        mock_network.name = "updated-network"
        mock_network.status = "ACTIVE"
        mock_network.description = "Updated description"
        mock_network.admin_state_up = False
        mock_network.shared = True
        mock_network.mtu = 1400
        mock_network.provider_network_type = "vxlan"
        mock_network.provider_physical_network = None
        mock_network.provider_segmentation_id = 300
        mock_network.project_id = "proj-update-123"

        # Configure mock network.update_network()
        mock_conn.network.update_network.return_value = mock_network

        # Test update_network()
        neutron_tools = self.get_neutron_tools()
        result = neutron_tools.update_network(
            network_id="net-update-123",
            name="updated-network",
            description="Updated description",
            is_admin_state_up=False,
            is_shared=True
        )
        
        # Verify results
        expected_network = Network(
            id="net-update-123",
            name="updated-network", 
            status="ACTIVE",
            description="Updated description",
            is_admin_state_up=False,
            is_shared=True,
            mtu=1400,
            provider_network_type="vxlan",
            provider_physical_network=None,
            provider_segmentation_id=300,
            project_id="proj-update-123"
        )
        
        assert result == expected_network

        # Verify mock calls
        expected_args = {
            'name': 'updated-network',
            'description': 'Updated description',
            'admin_state_up': False,
            'shared': True
        }
        mock_conn.network.update_network.assert_called_once_with("net-update-123", **expected_args)

    def test_update_network_partial_update(self, mock_openstack_connect_neutron):
        """Test updating a network with only some parameters."""
        mock_conn = mock_openstack_connect_neutron
        
        # Create mock updated network object
        mock_network = Mock()
        mock_network.id = "net-partial-123"
        mock_network.name = "new-name"
        mock_network.status = "ACTIVE"
        mock_network.description = "old description"
        mock_network.admin_state_up = True
        mock_network.shared = False
        mock_network.mtu = None
        mock_network.provider_network_type = None
        mock_network.provider_physical_network = None
        mock_network.provider_segmentation_id = None
        mock_network.project_id = None

        mock_conn.network.update_network.return_value = mock_network

        # Test update_network() with only name
        neutron_tools = self.get_neutron_tools()
        result = neutron_tools.update_network(
            network_id="net-partial-123",
            name="new-name"
        )
        
        # Verify results
        expected_network = Network(
            id="net-partial-123",
            name="new-name",
            status="ACTIVE", 
            description="old description",
            is_admin_state_up=True,
            is_shared=False,
            mtu=None,
            provider_network_type=None,
            provider_physical_network=None,
            provider_segmentation_id=None,
            project_id=None
        )
        
        assert result == expected_network

        # Verify mock calls - only name should be passed
        expected_args = {'name': 'new-name'}
        mock_conn.network.update_network.assert_called_once_with("net-partial-123", **expected_args)

    def test_update_network_no_parameters(self, mock_openstack_connect_neutron):
        """Test updating a network with no parameters provided."""
        mock_conn = mock_openstack_connect_neutron

        # Test update_network() with no update parameters
        neutron_tools = self.get_neutron_tools()
        
        # Verify exception is raised
        with pytest.raises(Exception, match="No update parameters provided"):
            neutron_tools.update_network("net-123")

        # Verify no network update call was made
        mock_conn.network.update_network.assert_not_called()



    def test_delete_network_success(self, mock_openstack_connect_neutron):
        """Test deleting a network successfully."""
        mock_conn = mock_openstack_connect_neutron
        
        # Create mock network object for initial get
        mock_network = Mock()
        mock_network.name = "network-to-delete"

        # Configure mock network.get_network() and delete_network()
        mock_conn.network.get_network.return_value = mock_network
        mock_conn.network.delete_network.return_value = None

        # Test delete_network()
        neutron_tools = self.get_neutron_tools()
        result = neutron_tools.delete_network("net-delete-123")
        
        # Verify results (successful deletion returns None)
        assert result is None

        # Verify mock calls
        mock_conn.network.get_network.assert_called_once_with("net-delete-123")
        mock_conn.network.delete_network.assert_called_once_with("net-delete-123", ignore_missing=False)

    def test_delete_network_not_found(self, mock_openstack_connect_neutron):
        """Test deleting a network when network not found."""
        mock_conn = mock_openstack_connect_neutron
        
        # Configure mock to return None (network not found)
        mock_conn.network.get_network.return_value = None

        # Test delete_network()
        neutron_tools = self.get_neutron_tools()
        
        # Verify exception is raised
        with pytest.raises(Exception, match="Network with ID nonexistent-net not found"):
            neutron_tools.delete_network("nonexistent-net")

        # Verify delete was not called
        mock_conn.network.delete_network.assert_not_called()


