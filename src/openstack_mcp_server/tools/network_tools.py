from fastmcp import FastMCP

from .base import get_openstack_conn
from .response.network import (
    FloatingIP,
    Network,
    Port,
    Subnet,
)


class NetworkTools:
    """
    A class to encapsulate Network-related tools and utilities.
    """

    def register_tools(self, mcp: FastMCP):
        """
        Register Network-related tools with the FastMCP instance.
        """

        mcp.tool()(self.get_networks)
        mcp.tool()(self.create_network)
        mcp.tool()(self.get_network_detail)
        mcp.tool()(self.update_network)
        mcp.tool()(self.delete_network)
        mcp.tool()(self.get_subnets)
        mcp.tool()(self.create_subnet)
        mcp.tool()(self.get_subnet_detail)
        mcp.tool()(self.update_subnet)
        mcp.tool()(self.delete_subnet)
        mcp.tool()(self.get_ports)
        mcp.tool()(self.create_port)
        mcp.tool()(self.get_port_detail)
        mcp.tool()(self.update_port)
        mcp.tool()(self.delete_port)
        mcp.tool()(self.add_port_fixed_ip)
        mcp.tool()(self.remove_port_fixed_ip)
        mcp.tool()(self.get_port_allowed_address_pairs)
        mcp.tool()(self.add_port_allowed_address_pair)
        mcp.tool()(self.remove_port_allowed_address_pair)
        mcp.tool()(self.set_port_binding)
        mcp.tool()(self.set_port_admin_state)
        mcp.tool()(self.toggle_port_admin_state)
        mcp.tool()(self.get_floating_ips)
        mcp.tool()(self.create_floating_ip)
        mcp.tool()(self.allocate_floating_ip_pool_to_project)
        mcp.tool()(self.attach_floating_ip_to_port)
        mcp.tool()(self.detach_floating_ip_from_port)
        mcp.tool()(self.delete_floating_ip)
        mcp.tool()(self.update_floating_ip_description)
        mcp.tool()(self.reassign_floating_ip_to_port)
        mcp.tool()(self.create_floating_ips_bulk)
        mcp.tool()(self.assign_first_available_floating_ip)
        mcp.tool()(self.set_subnet_gateway)
        mcp.tool()(self.clear_subnet_gateway)
        mcp.tool()(self.set_subnet_dhcp_enabled)
        mcp.tool()(self.toggle_subnet_dhcp)

    def get_networks(
        self,
        status_filter: str | None = None,
        shared_only: bool = False,
    ) -> list[Network]:
        """
        Get the list of Networks with optional filtering.

        :param status_filter: Filter networks by status (e.g., `ACTIVE`, `DOWN`)
        :param shared_only: If True, only show shared networks
        :return: List of Network objects
        """
        conn = get_openstack_conn()

        filters = {}

        if status_filter:
            filters["status"] = status_filter.upper()

        if shared_only:
            filters["shared"] = True

        networks = conn.list_networks(filters=filters)

        return [
            self._convert_to_network_model(network) for network in networks
        ]

    def create_network(
        self,
        name: str,
        description: str | None = None,
        is_admin_state_up: bool = True,
        is_shared: bool = False,
        provider_network_type: str | None = None,
        provider_physical_network: str | None = None,
        provider_segmentation_id: int | None = None,
    ) -> Network:
        """
        Create a new Network.

        :param name: Network name
        :param description: Network description
        :param is_admin_state_up: Administrative state
        :param is_shared: Whether the network is shared
        :param provider_network_type: Provider network type (e.g., 'vlan', 'flat', 'vxlan')
        :param provider_physical_network: Physical network name
        :param provider_segmentation_id: Segmentation ID for VLAN/VXLAN
        :return: Created Network object
        """
        conn = get_openstack_conn()

        network_args = {
            "name": name,
            "admin_state_up": is_admin_state_up,
            "shared": is_shared,
        }

        if description:
            network_args["description"] = description

        if provider_network_type:
            network_args["provider_network_type"] = provider_network_type

        if provider_physical_network:
            network_args["provider_physical_network"] = (
                provider_physical_network
            )

        if provider_segmentation_id is not None:
            network_args["provider_segmentation_id"] = provider_segmentation_id

        network = conn.network.create_network(**network_args)

        return self._convert_to_network_model(network)

    def get_network_detail(self, network_id: str) -> Network:
        """
        Get detailed information about a specific Network.

        :param network_id: ID of the network to retrieve
        :return: Network details
        """
        conn = get_openstack_conn()

        network = conn.network.get_network(network_id)
        return self._convert_to_network_model(network)

    def update_network(
        self,
        network_id: str,
        name: str | None = None,
        description: str | None = None,
        is_admin_state_up: bool | None = None,
        is_shared: bool | None = None,
    ) -> Network:
        """
        Update an existing Network.

        :param network_id: ID of the network to update
        :param name: New network name
        :param description: New network description
        :param is_admin_state_up: New administrative state
        :param is_shared: New shared state
        :return: Updated Network object
        """
        conn = get_openstack_conn()

        update_args = {}

        if name is not None:
            update_args["name"] = name
        if description is not None:
            update_args["description"] = description
        if is_admin_state_up is not None:
            update_args["admin_state_up"] = is_admin_state_up
        if is_shared is not None:
            update_args["shared"] = is_shared

        if not update_args:
            current = conn.network.get_network(network_id)
            return self._convert_to_network_model(current)
        network = conn.network.update_network(network_id, **update_args)
        return self._convert_to_network_model(network)

    def delete_network(self, network_id: str) -> None:
        """
        Delete a Network.

        :param network_id: ID of the network to delete
        :return: None
        """
        conn = get_openstack_conn()
        conn.network.delete_network(network_id, ignore_missing=False)

        return None

    def _convert_to_network_model(self, openstack_network) -> Network:
        """
        Convert an OpenStack network object to a Network pydantic model.

        :param openstack_network: OpenStack network object
        :type openstack_network: Any
        :return: Pydantic Network model
        """
        return Network(
            id=openstack_network.id,
            name=openstack_network.name or "",
            status=openstack_network.status or "",
            description=openstack_network.description or None,
            is_admin_state_up=openstack_network.is_admin_state_up or False,
            is_shared=openstack_network.is_shared or False,
            mtu=openstack_network.mtu or None,
            provider_network_type=openstack_network.provider_network_type
            or None,
            provider_physical_network=openstack_network.provider_physical_network
            or None,
            provider_segmentation_id=openstack_network.provider_segmentation_id
            or None,
            project_id=openstack_network.project_id or None,
        )

    def get_subnets(
        self,
        network_id: str | None = None,
        ip_version: int | None = None,
        project_id: str | None = None,
        has_gateway: bool | None = None,
        is_dhcp_enabled: bool | None = None,
    ) -> list[Subnet]:
        """
        Get the list of Subnets with optional filtering.

        :param network_id: Filter by network ID
        :param ip_version: Filter by IP version (e.g., 4, 6)
        :param project_id: Filter by project ID
        :param has_gateway: Filter by whether a gateway is set
        :param is_dhcp_enabled: Filter by DHCP enabled state
        :return: List of Subnet objects
        """
        conn = get_openstack_conn()
        filters: dict = {}
        if network_id:
            filters["network_id"] = network_id
        if ip_version is not None:
            filters["ip_version"] = ip_version
        if project_id:
            filters["project_id"] = project_id
        if is_dhcp_enabled is not None:
            filters["enable_dhcp"] = is_dhcp_enabled
        subnets = conn.list_subnets(filters=filters)
        if has_gateway is not None:
            subnets = [
                s for s in subnets if (s.gateway_ip is not None) == has_gateway
            ]
        return [self._convert_to_subnet_model(subnet) for subnet in subnets]

    def create_subnet(
        self,
        network_id: str,
        cidr: str,
        name: str | None = None,
        ip_version: int = 4,
        gateway_ip: str | None = None,
        is_dhcp_enabled: bool = True,
        description: str | None = None,
        dns_nameservers: list[str] | None = None,
        allocation_pools: list[dict] | None = None,
        host_routes: list[dict] | None = None,
    ) -> Subnet:
        """
        Create a new Subnet.

        :param network_id: ID of the parent network
        :param cidr: Subnet CIDR
        :param name: Subnet name
        :param ip_version: IP version
        :param gateway_ip: Gateway IP address
        :param is_dhcp_enabled: Whether DHCP is enabled
        :param description: Subnet description
        :param dns_nameservers: DNS nameserver list
        :param allocation_pools: Allocation pool list
        :param host_routes: Static host routes
        :return: Created Subnet object
        """
        conn = get_openstack_conn()
        subnet_args: dict = {
            "network_id": network_id,
            "cidr": cidr,
            "ip_version": ip_version,
            "enable_dhcp": is_dhcp_enabled,
        }
        if name is not None:
            subnet_args["name"] = name
        if description is not None:
            subnet_args["description"] = description
        if gateway_ip is not None:
            subnet_args["gateway_ip"] = gateway_ip
        if dns_nameservers is not None:
            subnet_args["dns_nameservers"] = dns_nameservers
        if allocation_pools is not None:
            subnet_args["allocation_pools"] = allocation_pools
        if host_routes is not None:
            subnet_args["host_routes"] = host_routes
        subnet = conn.network.create_subnet(**subnet_args)
        return self._convert_to_subnet_model(subnet)

    def get_subnet_detail(self, subnet_id: str) -> Subnet:
        """
        Get detailed information about a specific Subnet.

        :param subnet_id: ID of the subnet to retrieve
        :return: Subnet details
        """
        conn = get_openstack_conn()
        subnet = conn.network.get_subnet(subnet_id)
        return self._convert_to_subnet_model(subnet)

    def update_subnet(
        self,
        subnet_id: str,
        name: str | None = None,
        description: str | None = None,
        gateway_ip: str | None = None,
        is_dhcp_enabled: bool | None = None,
        dns_nameservers: list[str] | None = None,
        allocation_pools: list[dict] | None = None,
        host_routes: list[dict] | None = None,
    ) -> Subnet:
        """
        Update an existing Subnet.

        :param subnet_id: ID of the subnet to update
        :param name: New subnet name
        :param description: New subnet description
        :param gateway_ip: New gateway IP
        :param is_dhcp_enabled: DHCP enabled state
        :param dns_nameservers: DNS nameserver list
        :param allocation_pools: Allocation pool list
        :param host_routes: Static host routes
        :return: Updated Subnet object
        """
        conn = get_openstack_conn()
        update_args: dict = {}
        if name is not None:
            update_args["name"] = name
        if description is not None:
            update_args["description"] = description
        if gateway_ip is not None:
            update_args["gateway_ip"] = gateway_ip
        if is_dhcp_enabled is not None:
            update_args["enable_dhcp"] = is_dhcp_enabled
        if dns_nameservers is not None:
            update_args["dns_nameservers"] = dns_nameservers
        if allocation_pools is not None:
            update_args["allocation_pools"] = allocation_pools
        if host_routes is not None:
            update_args["host_routes"] = host_routes
        if not update_args:
            current = conn.network.get_subnet(subnet_id)
            return self._convert_to_subnet_model(current)
        subnet = conn.network.update_subnet(subnet_id, **update_args)
        return self._convert_to_subnet_model(subnet)

    def delete_subnet(self, subnet_id: str) -> None:
        """
        Delete a Subnet.

        :param subnet_id: ID of the subnet to delete
        :return: None
        """
        conn = get_openstack_conn()
        conn.network.delete_subnet(subnet_id, ignore_missing=False)
        return None

    def set_subnet_gateway(self, subnet_id: str, gateway_ip: str) -> Subnet:
        """
        Set or update a subnet's gateway IP.

        :param subnet_id: Subnet ID
        :param gateway_ip: Gateway IP to set
        :return: Updated Subnet object
        """
        conn = get_openstack_conn()
        subnet = conn.network.update_subnet(subnet_id, gateway_ip=gateway_ip)
        return self._convert_to_subnet_model(subnet)

    def clear_subnet_gateway(self, subnet_id: str) -> Subnet:
        """
        Clear a subnet's gateway IP (set to `None`).

        :param subnet_id: Subnet ID
        :return: Updated Subnet object
        """
        conn = get_openstack_conn()
        subnet = conn.network.update_subnet(subnet_id, gateway_ip=None)
        return self._convert_to_subnet_model(subnet)

    def set_subnet_dhcp_enabled(self, subnet_id: str, enabled: bool) -> Subnet:
        """
        Enable or disable DHCP on a subnet.

        :param subnet_id: Subnet ID
        :param enabled: DHCP enabled state
        :return: Updated Subnet object
        """
        conn = get_openstack_conn()
        subnet = conn.network.update_subnet(subnet_id, enable_dhcp=enabled)
        return self._convert_to_subnet_model(subnet)

    def toggle_subnet_dhcp(self, subnet_id: str) -> Subnet:
        """
        Toggle DHCP enabled state for a subnet.

        :param subnet_id: Subnet ID
        :return: Updated Subnet object
        """
        conn = get_openstack_conn()
        current = conn.network.get_subnet(subnet_id)
        subnet = conn.network.update_subnet(
            subnet_id,
            enable_dhcp=not current.enable_dhcp,
        )
        return self._convert_to_subnet_model(subnet)

    def _convert_to_subnet_model(self, openstack_subnet) -> Subnet:
        """
        Convert an OpenStack subnet object to a Subnet pydantic model.

        :param openstack_subnet: OpenStack subnet object
        :return: Pydantic Subnet model
        """
        return Subnet(
            id=openstack_subnet.id,
            name=openstack_subnet.name,
            status=openstack_subnet.status,
            description=openstack_subnet.description,
            project_id=openstack_subnet.project_id,
            network_id=openstack_subnet.network_id,
            cidr=openstack_subnet.cidr,
            ip_version=openstack_subnet.ip_version,
            gateway_ip=openstack_subnet.gateway_ip,
            is_dhcp_enabled=openstack_subnet.enable_dhcp,
            allocation_pools=openstack_subnet.allocation_pools,
            dns_nameservers=openstack_subnet.dns_nameservers,
            host_routes=openstack_subnet.host_routes,
        )

    def get_ports(
        self,
        status_filter: str | None = None,
        device_id: str | None = None,
        network_id: str | None = None,
    ) -> list[Port]:
        """
        Get the list of Ports with optional filtering.

        :param status_filter: Filter by port status (e.g., `ACTIVE`, `DOWN`)
        :param device_id: Filter by device ID
        :param network_id: Filter by network ID
        :return: List of Port objects
        """
        conn = get_openstack_conn()
        filters: dict = {}
        if status_filter:
            filters["status"] = status_filter.upper()
        if device_id:
            filters["device_id"] = device_id
        if network_id:
            filters["network_id"] = network_id
        ports = conn.list_ports(filters=filters)
        return [self._convert_to_port_model(port) for port in ports]

    def add_port_fixed_ip(
        self,
        port_id: str,
        subnet_id: str | None = None,
        ip_address: str | None = None,
    ) -> Port:
        """
        Add a fixed IP to a port.

        :param port_id: Target port ID
        :param subnet_id: Subnet ID of the fixed IP entry
        :param ip_address: Fixed IP address to add
        :return: Updated Port object
        """
        conn = get_openstack_conn()
        port = conn.network.get_port(port_id)
        fixed_ips = list(port.fixed_ips or [])
        entry: dict = {}
        if subnet_id is not None:
            entry["subnet_id"] = subnet_id
        if ip_address is not None:
            entry["ip_address"] = ip_address
        fixed_ips.append(entry)
        updated = conn.network.update_port(port_id, fixed_ips=fixed_ips)
        return self._convert_to_port_model(updated)

    def remove_port_fixed_ip(
        self,
        port_id: str,
        ip_address: str | None = None,
        subnet_id: str | None = None,
    ) -> Port:
        """
        Remove a fixed IP entry from a port.

        :param port_id: Target port ID
        :param ip_address: Fixed IP address to remove
        :param subnet_id: Subnet ID of the entry to remove
        :return: Updated Port object
        """
        conn = get_openstack_conn()
        port = conn.network.get_port(port_id)
        current = list(port.fixed_ips or [])
        if not current:
            return self._convert_to_port_model(port)

        def predicate(item: dict) -> bool:
            if ip_address is not None and item.get("ip_address") == ip_address:
                return False
            if subnet_id is not None and item.get("subnet_id") == subnet_id:
                return False
            return True

        new_fixed = [fi for fi in current if predicate(fi)]
        updated = conn.network.update_port(port_id, fixed_ips=new_fixed)
        return self._convert_to_port_model(updated)

    def get_port_allowed_address_pairs(self, port_id: str) -> list[dict]:
        """
        Get allowed address pairs configured on a port.

        :param port_id: Port ID
        :return: Allowed address pairs
        """
        conn = get_openstack_conn()
        port = conn.network.get_port(port_id)
        return list(port.allowed_address_pairs or [])

    def add_port_allowed_address_pair(
        self,
        port_id: str,
        ip_address: str,
        mac_address: str | None = None,
    ) -> Port:
        """
        Add an allowed address pair to a port.

        :param port_id: Port ID
        :param ip_address: IP address to allow
        :param mac_address: MAC address to allow
        :return: Updated Port object
        """
        conn = get_openstack_conn()
        port = conn.network.get_port(port_id)

        pairs = list(port.allowed_address_pairs or [])
        entry = {"ip_address": ip_address}
        if mac_address is not None:
            entry["mac_address"] = mac_address
        pairs.append(entry)

        updated = conn.network.update_port(
            port_id,
            allowed_address_pairs=pairs,
        )
        return self._convert_to_port_model(updated)

    def remove_port_allowed_address_pair(
        self,
        port_id: str,
        ip_address: str,
        mac_address: str | None = None,
    ) -> Port:
        """
        Remove an allowed address pair from a port.

        :param port_id: Port ID
        :param ip_address: IP address to remove
        :param mac_address: MAC address to remove. If not provided, remove all pairs with the IP
        :return: Updated Port object
        """
        conn = get_openstack_conn()
        port = conn.network.get_port(port_id)
        pairs = list(port.allowed_address_pairs or [])

        def keep(p: dict) -> bool:
            if mac_address is None:
                return p.get("ip_address") != ip_address
            return not (
                p.get("ip_address") == ip_address
                and p.get("mac_address") == mac_address
            )

        new_pairs = [p for p in pairs if keep(p)]
        updated = conn.network.update_port(
            port_id,
            allowed_address_pairs=new_pairs,
        )
        return self._convert_to_port_model(updated)

    def set_port_binding(
        self,
        port_id: str,
        host_id: str | None = None,
        vnic_type: str | None = None,
        profile: dict | None = None,
    ) -> Port:
        """
        Set binding attributes for a port.

        :param port_id: Port ID
        :param host_id: Binding host ID
        :param vnic_type: VNIC type
        :param profile: Binding profile
        :return: Updated Port object
        """
        conn = get_openstack_conn()
        update_args: dict = {}
        if host_id is not None:
            update_args["binding_host_id"] = host_id
        if vnic_type is not None:
            update_args["binding_vnic_type"] = vnic_type
        if profile is not None:
            update_args["binding_profile"] = profile
        if not update_args:
            current = conn.network.get_port(port_id)
            return self._convert_to_port_model(current)
        updated = conn.network.update_port(port_id, **update_args)
        return self._convert_to_port_model(updated)

    def set_port_admin_state(
        self,
        port_id: str,
        is_admin_state_up: bool,
    ) -> Port:
        """
        Set the administrative state of a port.

        :param port_id: Port ID
        :param is_admin_state_up: Administrative state
        :return: Updated Port object
        """
        conn = get_openstack_conn()
        updated = conn.network.update_port(
            port_id,
            admin_state_up=is_admin_state_up,
        )
        return self._convert_to_port_model(updated)

    def toggle_port_admin_state(self, port_id: str) -> Port:
        """
        Toggle the administrative state of a port.

        :param port_id: Port ID
        :return: Updated Port object
        """
        conn = get_openstack_conn()
        current = conn.network.get_port(port_id)
        updated = conn.network.update_port(
            port_id,
            admin_state_up=not current.admin_state_up,
        )
        return self._convert_to_port_model(updated)

    def create_port(
        self,
        network_id: str,
        name: str | None = None,
        description: str | None = None,
        is_admin_state_up: bool = True,
        device_id: str | None = None,
        fixed_ips: list[dict] | None = None,
        security_group_ids: list[str] | None = None,
    ) -> Port:
        """
        Create a new Port.

        :param network_id: ID of the parent network
        :param name: Port name
        :param description: Port description
        :param is_admin_state_up: Administrative state
        :param device_id: Device ID
        :param fixed_ips: Fixed IP list
        :param security_group_ids: Security group ID list
        :return: Created Port object
        """
        conn = get_openstack_conn()
        port_args: dict = {
            "network_id": network_id,
            "admin_state_up": is_admin_state_up,
        }
        if name is not None:
            port_args["name"] = name
        if description is not None:
            port_args["description"] = description
        if device_id is not None:
            port_args["device_id"] = device_id
        if fixed_ips is not None:
            port_args["fixed_ips"] = fixed_ips
        if security_group_ids is not None:
            port_args["security_groups"] = security_group_ids
        port = conn.network.create_port(**port_args)
        return self._convert_to_port_model(port)

    def get_port_detail(self, port_id: str) -> Port:
        """
        Get detailed information about a specific Port.

        :param port_id: ID of the port to retrieve
        :return: Port details
        """
        conn = get_openstack_conn()
        port = conn.network.get_port(port_id)
        return self._convert_to_port_model(port)

    def update_port(
        self,
        port_id: str,
        name: str | None = None,
        description: str | None = None,
        is_admin_state_up: bool | None = None,
        device_id: str | None = None,
        security_group_ids: list[str] | None = None,
    ) -> Port:
        """
        Update an existing Port.

        :param port_id: ID of the port to update
        :param name: New port name
        :param description: New port description
        :param is_admin_state_up: Administrative state
        :param device_id: Device ID
        :param security_group_ids: Security group ID list
        :return: Updated Port object
        """
        conn = get_openstack_conn()
        update_args: dict = {}
        if name is not None:
            update_args["name"] = name
        if description is not None:
            update_args["description"] = description
        if is_admin_state_up is not None:
            update_args["admin_state_up"] = is_admin_state_up
        if device_id is not None:
            update_args["device_id"] = device_id
        if security_group_ids is not None:
            update_args["security_groups"] = security_group_ids
        if not update_args:
            current = conn.network.get_port(port_id)
            return self._convert_to_port_model(current)
        port = conn.network.update_port(port_id, **update_args)
        return self._convert_to_port_model(port)

    def delete_port(self, port_id: str) -> None:
        """
        Delete a Port.

        :param port_id: ID of the port to delete
        :return: None
        """
        conn = get_openstack_conn()
        conn.network.delete_port(port_id, ignore_missing=False)
        return None

    def _convert_to_port_model(self, openstack_port) -> Port:
        """
        Convert an OpenStack Port object to a Port pydantic model.

        :param openstack_port: OpenStack port object
        :return: Pydantic Port model
        """
        return Port(
            id=openstack_port.id,
            name=openstack_port.name,
            status=openstack_port.status,
            description=openstack_port.description,
            project_id=openstack_port.project_id,
            network_id=openstack_port.network_id,
            is_admin_state_up=openstack_port.admin_state_up,
            device_id=openstack_port.device_id,
            device_owner=openstack_port.device_owner,
            mac_address=openstack_port.mac_address,
            fixed_ips=openstack_port.fixed_ips,
            security_group_ids=openstack_port.security_group_ids
            if hasattr(openstack_port, "security_group_ids")
            else None,
        )

    def get_floating_ips(
        self,
        status_filter: str | None = None,
        project_id: str | None = None,
        port_id: str | None = None,
        floating_network_id: str | None = None,
        unassigned_only: bool | None = None,
    ) -> list[FloatingIP]:
        """
        Get the list of Floating IPs with optional filtering.

        :param status_filter: Filter by IP status (e.g., `ACTIVE`)
        :param project_id: Filter by project ID
        :param port_id: Filter by attached port ID
        :param floating_network_id: Filter by external network ID
        :param unassigned_only: If True, return only unassigned IPs
        :return: List of FloatingIP objects
        """
        conn = get_openstack_conn()
        filters: dict = {}
        if status_filter:
            filters["status"] = status_filter.upper()
        if project_id:
            filters["project_id"] = project_id
        if port_id:
            filters["port_id"] = port_id
        if floating_network_id:
            filters["floating_network_id"] = floating_network_id
        ips = list(conn.network.ips(**filters))
        if unassigned_only:
            ips = [i for i in ips if not i.port_id]
        return [self._convert_to_floating_ip_model(ip) for ip in ips]

    def create_floating_ip(
        self,
        floating_network_id: str,
        description: str | None = None,
        fixed_ip_address: str | None = None,
        port_id: str | None = None,
        project_id: str | None = None,
    ) -> FloatingIP:
        """
        Create a new Floating IP.

        :param floating_network_id: External (floating) network ID
        :param description: Floating IP description
        :param fixed_ip_address: Internal fixed IP to map
        :param port_id: Port ID to attach
        :param project_id: Project ID
        :return: Created FloatingIP object
        """
        conn = get_openstack_conn()
        ip_args: dict = {"floating_network_id": floating_network_id}
        if description is not None:
            ip_args["description"] = description
        if fixed_ip_address is not None:
            ip_args["fixed_ip_address"] = fixed_ip_address
        if port_id is not None:
            ip_args["port_id"] = port_id
        if project_id is not None:
            ip_args["project_id"] = project_id
        ip = conn.network.create_ip(**ip_args)
        return self._convert_to_floating_ip_model(ip)

    def allocate_floating_ip_pool_to_project(
        self,
        floating_network_id: str,
        project_id: str,
    ) -> None:
        """
        Allocate Floating IP pool (external network access) to a project via RBAC.

        :param floating_network_id: External network ID
        :param project_id: Target project ID
        :return: None
        """
        conn = get_openstack_conn()
        conn.network.create_rbac_policy(
            object_type="network",
            object_id=floating_network_id,
            action="access_as_external",
            target_project_id=project_id,
        )
        return None

    def attach_floating_ip_to_port(
        self,
        floating_ip_id: str,
        port_id: str,
        fixed_ip_address: str | None = None,
    ) -> FloatingIP:
        """
        Attach a Floating IP to a Port.

        :param floating_ip_id: Floating IP ID
        :param port_id: Port ID to attach
        :param fixed_ip_address: Specific fixed IP on the port (optional)
        :return: Updated Floating IP object
        """
        conn = get_openstack_conn()
        update_args: dict = {"port_id": port_id}
        if fixed_ip_address is not None:
            update_args["fixed_ip_address"] = fixed_ip_address
        ip = conn.network.update_ip(floating_ip_id, **update_args)
        return self._convert_to_floating_ip_model(ip)

    def detach_floating_ip_from_port(self, floating_ip_id: str) -> FloatingIP:
        """
        Detach a Floating IP from its Port.

        :param floating_ip_id: Floating IP ID
        :return: Updated FloatingIP object
        """
        conn = get_openstack_conn()
        ip = conn.network.update_ip(floating_ip_id, port_id=None)
        return self._convert_to_floating_ip_model(ip)

    def delete_floating_ip(self, floating_ip_id: str) -> None:
        """
        Delete a Floating IP.

        :param floating_ip_id: Floating IP ID to delete
        :return: None
        """
        conn = get_openstack_conn()
        conn.network.delete_ip(floating_ip_id, ignore_missing=False)
        return None

    def update_floating_ip_description(
        self,
        floating_ip_id: str,
        description: str | None,
    ) -> FloatingIP:
        """
        Update a Floating IP's description.

        :param floating_ip_id: Floating IP ID
        :param description: New description (`None` to clear)
        :return: Updated FloatingIP object
        """
        conn = get_openstack_conn()
        ip = conn.network.update_ip(floating_ip_id, description=description)
        return self._convert_to_floating_ip_model(ip)

    def reassign_floating_ip_to_port(
        self,
        floating_ip_id: str,
        port_id: str,
        fixed_ip_address: str | None = None,
    ) -> FloatingIP:
        """
        Reassign a Floating IP to a different Port.

        :param floating_ip_id: Floating IP ID
        :param port_id: New port ID to attach
        :param fixed_ip_address: Specific fixed IP on the port (optional)
        :return: Updated Floating IP object
        """
        conn = get_openstack_conn()
        update_args: dict = {"port_id": port_id}
        if fixed_ip_address is not None:
            update_args["fixed_ip_address"] = fixed_ip_address
        ip = conn.network.update_ip(floating_ip_id, **update_args)
        return self._convert_to_floating_ip_model(ip)

    def create_floating_ips_bulk(
        self,
        floating_network_id: str,
        count: int,
    ) -> list[FloatingIP]:
        """
        Create multiple floating IPs on the specified external network.

        :param floating_network_id: External network ID
        :param count: Number of floating IPs to create (negative treated as 0)
        :return: List of created FloatingIP objects
        """
        conn = get_openstack_conn()
        created = []
        for _ in range(max(0, count)):
            ip = conn.network.create_ip(
                floating_network_id=floating_network_id,
            )
            created.append(self._convert_to_floating_ip_model(ip))
        return created

    def assign_first_available_floating_ip(
        self,
        floating_network_id: str,
        port_id: str,
    ) -> FloatingIP:
        """
        Assign the first available floating IP from a network to a port.
        If none are available, create a new one and assign it.

        :param floating_network_id: External network ID
        :param port_id: Target port ID
        :return: Updated FloatingIP object
        """
        conn = get_openstack_conn()
        existing = list(
            conn.network.ips(floating_network_id=floating_network_id),
        )
        available = next(
            (i for i in existing if not i.port_id),
            None,
        )
        if available is None:
            created = conn.network.create_ip(
                floating_network_id=floating_network_id,
            )
            target_id = created.id
        else:
            target_id = available.id
        ip = conn.network.update_ip(target_id, port_id=port_id)
        return self._convert_to_floating_ip_model(ip)

    def _convert_to_floating_ip_model(self, openstack_ip) -> FloatingIP:
        """
        Convert an OpenStack floating IP object to a FloatingIP pydantic model.

        :param openstack_ip: OpenStack floating IP object
        :return: Pydantic FloatingIP model
        """
        return FloatingIP(
            id=openstack_ip.id,
            name=openstack_ip.name,
            status=openstack_ip.status,
            description=openstack_ip.description,
            project_id=openstack_ip.project_id,
            floating_ip_address=openstack_ip.floating_ip_address,
            floating_network_id=openstack_ip.floating_network_id,
            fixed_ip_address=openstack_ip.fixed_ip_address,
            port_id=openstack_ip.port_id,
            router_id=openstack_ip.router_id,
        )
