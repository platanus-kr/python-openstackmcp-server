from typing import List
import openstack
from pydantic import BaseModel
from fastmcp import FastMCP
from .base import get_openstack_conn


class Network(BaseModel):
    id: str
    name: str
    status: str
    description: str | None = None
    is_admin_state_up: bool = True
    is_shared: bool = False
    mtu: int | None = None
    provider_network_type: str | None = None
    provider_physical_network: str | None = None
    provider_segmentation_id: int | None = None
    project_id: str | None = None

class Subnet(BaseModel):
    id: str
    name: str
    status: str

class Port(BaseModel):
    id: str
    name: str
    status: str

class Router(BaseModel):
    id: str
    name: str
    status: str

class SecurityGroup(BaseModel):
    id: str
    name: str
    status: str

class SecurityGroupRule(BaseModel):
    id: str
    name: str
    status: str

class FloatingIP(BaseModel):
    id: str
    name: str
    status: str



class NeutronTools:
    """
    A class to encapsulate Neutron-related tools and utilities.
    """

    def _convert_to_network_model(self, openstack_network) -> Network:
        """
        Convert an OpenStack network object to a Network pydantic model.
        
        Args:
            openstack_network: OpenStack network object
            
        Returns:
            Network pydantic model
        """
        return Network(
            id=openstack_network.id,
            name=openstack_network.name or "",
            status=openstack_network.status or "",
            description=getattr(openstack_network, 'description', None),
            is_admin_state_up=getattr(openstack_network, 'admin_state_up', True),
            is_shared=getattr(openstack_network, 'shared', False),
            mtu=getattr(openstack_network, 'mtu', None),
            provider_network_type=getattr(openstack_network, 'provider_network_type', None),
            provider_physical_network=getattr(openstack_network, 'provider_physical_network', None),
            provider_segmentation_id=getattr(openstack_network, 'provider_segmentation_id', None),
            project_id=getattr(openstack_network, 'project_id', None)
        )

    def register_tools(self, mcp: FastMCP):
        """
        Register Neutron-related tools with the FastMCP instance.
        """

        mcp.tool()(self.get_neutron_networks)
        mcp.tool()(self.create_network)
        mcp.tool()(self.get_network_detail)
        mcp.tool()(self.update_network)
        mcp.tool()(self.delete_network)

    def get_neutron_networks(
        self, 
        status_filter: str | None = None,
        shared_only: bool = False
    ) -> List[Network]:
        """
        Get the list of Neutron networks with optional filtering.
        
        Args:
            status_filter: Filter networks by status (e.g., 'ACTIVE', 'DOWN')
            shared_only: If True, only show shared networks
            
        Returns:
            List of Network objects
        """
        conn = get_openstack_conn()
        
        try:
            networks = conn.list_networks()
            
            # Apply filters
            if status_filter:
                networks = [net for net in networks if net.status.upper() == status_filter.upper()]
                
            if shared_only:
                networks = [net for net in networks if net.shared]
            
            # Convert OpenStack networks to Network models
            return [self._convert_to_network_model(network) for network in networks]
            
        except Exception as e:
            # Return empty list on error, or raise exception for better error handling
            raise Exception(f"Failed to retrieve networks: {str(e)}")

    def create_network(
        self, 
        name: str, 
        description: str | None = None,
        is_admin_state_up: bool = True,
        is_shared: bool = False,
        provider_network_type: str | None = None,
        provider_physical_network: str | None = None,
        provider_segmentation_id: int | None = None
    ) -> Network:
        """
        Create a new Neutron network.
        
        Args:
            name: Network name
            description: Network description
            is_admin_state_up: Administrative state
            is_shared: Whether the network is shared
            provider_network_type: Provider network type (e.g., 'vlan', 'flat', 'vxlan')
            provider_physical_network: Physical network name
            provider_segmentation_id: Segmentation ID for VLAN/VXLAN
        
        Returns:
            Created Network object
        """
        conn = get_openstack_conn()
        
        try:
            network_args = {
                'name': name,
                'admin_state_up': is_admin_state_up,
                'shared': is_shared,
            }
            
            if description:
                network_args['description'] = description
            
            if provider_network_type:
                network_args['provider_network_type'] = provider_network_type
            
            if provider_physical_network:
                network_args['provider_physical_network'] = provider_physical_network
                
            if provider_segmentation_id is not None:
                network_args['provider_segmentation_id'] = provider_segmentation_id
                
            network = conn.network.create_network(**network_args)
            
            return self._convert_to_network_model(network)
            
        except Exception as e:
            raise Exception(f"Failed to create network: {str(e)}")

    def get_network_detail(self, network_id: str) -> Network:
        """
        Get detailed information about a specific Neutron network.
        
        Args:
            network_id: ID of the network to retrieve
            
        Returns:
            Network object with detailed information
        """
        conn = get_openstack_conn()
        
        try:
            network = conn.network.get_network(network_id)
            if not network:
                raise Exception(f"Network with ID {network_id} not found")
                
            return self._convert_to_network_model(network)
            
        except Exception as e:
            raise Exception(f"Failed to retrieve network details: {str(e)}")

    def update_network(
        self, 
        network_id: str,
        name: str | None = None,
        description: str | None = None,
        is_admin_state_up: bool | None = None,
        is_shared: bool | None = None
    ) -> Network:
        """
        Update an existing Neutron network.
        
        Args:
            network_id: ID of the network to update
            name: New network name
            description: New network description
            is_admin_state_up: New administrative state
            is_shared: New shared state
            
        Returns:
            Updated Network object
        """
        conn = get_openstack_conn()
        
        try:
            update_args = {}
            
            if name is not None:
                update_args['name'] = name
            if description is not None:
                update_args['description'] = description
            if is_admin_state_up is not None:
                update_args['admin_state_up'] = is_admin_state_up
            if is_shared is not None:
                update_args['shared'] = is_shared
                
            if not update_args:
                raise Exception("No update parameters provided")
                
            network = conn.network.update_network(network_id, **update_args)
            
            return self._convert_to_network_model(network)
            
        except Exception as e:
            raise Exception(f"Failed to update network: {str(e)}")

    def delete_network(self, network_id: str) -> str:
        """
        Delete a Neutron network.
        
        Args:
            network_id: ID of the network to delete
            
        Returns:
            Confirmation message
        """
        conn = get_openstack_conn()
        
        try:
            # First, get network details for confirmation
            network = conn.network.get_network(network_id)
            if not network:
                raise Exception(f"Network with ID {network_id} not found")
                
            network_name = network.name
            
            # Delete the network
            conn.network.delete_network(network_id, ignore_missing=False)
            
            return f"Network '{network_name}' (ID: {network_id}) deleted successfully"
            
        except Exception as e:
            if "Network with ID" in str(e) and "not found" in str(e):
                # Re-raise our own not found exception
                raise e
            else:
                # Wrap other exceptions
                raise Exception(f"Failed to delete network: {str(e)}")