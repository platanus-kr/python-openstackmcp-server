import pytest
from unittest.mock import Mock
from openstack import exceptions
from openstack_mcp_server.tools.neutron_tools import NeutronTools, Network


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
        mock_conn.list_networks.assert_called_once()

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
        mock_conn.list_networks.assert_called_once()

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
        
        mock_conn.list_networks.return_value = [mock_network1, mock_network2]

        # Test get_neutron_networks() with status filter
        neutron_tools = self.get_neutron_tools()
        result = neutron_tools.get_neutron_networks(status_filter="ACTIVE")
        
        # Verify only ACTIVE network is returned
        assert len(result) == 1
        assert result[0].id == "net-active"
        assert result[0].status == "ACTIVE"

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
        
        mock_conn.list_networks.return_value = [mock_network1, mock_network2]

        # Test get_neutron_networks() with shared_only filter
        neutron_tools = self.get_neutron_tools()
        result = neutron_tools.get_neutron_networks(shared_only=True)
        
        # Verify only shared network is returned
        assert len(result) == 1
        assert result[0].id == "net-shared"
        assert result[0].is_shared is True

    def test_get_neutron_networks_exception(self, mock_openstack_connect_neutron):
        """Test get_neutron_networks when an exception occurs."""
        mock_conn = mock_openstack_connect_neutron
        
        # Configure mock to raise exception
        mock_conn.list_networks.side_effect = exceptions.HttpException("Connection failed")

        # Test get_neutron_networks()
        neutron_tools = self.get_neutron_tools()
        
        # Verify exception is raised
        with pytest.raises(Exception, match="Failed to retrieve networks: Connection failed"):
            neutron_tools.get_neutron_networks()

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

    def test_create_network_exception(self, mock_openstack_connect_neutron):
        """Test create_network when an exception occurs."""
        mock_conn = mock_openstack_connect_neutron
        
        # Configure mock to raise exception
        mock_conn.network.create_network.side_effect = exceptions.BadRequestException("Invalid network name")

        # Test create_network()
        neutron_tools = self.get_neutron_tools()
        
        # Verify exception is raised
        with pytest.raises(Exception, match="Failed to create network: Invalid network name"):
            neutron_tools.create_network(name="invalid-name")

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

    def test_get_network_detail_exception(self, mock_openstack_connect_neutron):
        """Test get_network_detail when an exception occurs."""
        mock_conn = mock_openstack_connect_neutron
        
        # Configure mock to raise exception
        mock_conn.network.get_network.side_effect = exceptions.HttpException("Connection failed")

        # Test get_network_detail()
        neutron_tools = self.get_neutron_tools()
        
        # Verify exception is raised
        with pytest.raises(Exception, match="Failed to retrieve network details: Connection failed"):
            neutron_tools.get_network_detail("some-net-id")

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

    def test_update_network_exception(self, mock_openstack_connect_neutron):
        """Test update_network when an exception occurs."""
        mock_conn = mock_openstack_connect_neutron
        
        # Configure mock to raise exception
        mock_conn.network.update_network.side_effect = exceptions.NotFoundException("Network not found")

        # Test update_network()
        neutron_tools = self.get_neutron_tools()
        
        # Verify exception is raised
        with pytest.raises(Exception, match="Failed to update network: Network not found"):
            neutron_tools.update_network("nonexistent-net", name="new-name")

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
        
        # Verify results
        expected_message = "Network 'network-to-delete' (ID: net-delete-123) deleted successfully"
        assert result == expected_message

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

    def test_delete_network_exception(self, mock_openstack_connect_neutron):
        """Test delete_network when an exception occurs during deletion."""
        mock_conn = mock_openstack_connect_neutron
        
        # Create mock network object for initial get
        mock_network = Mock()
        mock_network.name = "network-delete-fail"
        mock_conn.network.get_network.return_value = mock_network
        
        # Configure mock to raise exception during delete
        mock_conn.network.delete_network.side_effect = exceptions.ConflictException("Network in use")

        # Test delete_network()
        neutron_tools = self.get_neutron_tools()
        
        # Verify exception is raised
        with pytest.raises(Exception, match="Failed to delete network: Network in use"):
            neutron_tools.delete_network("net-in-use-123")
