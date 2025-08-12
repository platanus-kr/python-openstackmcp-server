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
    A class to encapsulate Neutron-related tools and utilities.
    """

    def register_tools(self, mcp: FastMCP):
        """
        Register Neutron-related tools with the FastMCP instance.
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
        Get the list of Neutron networks with optional filtering.

        Args:
            status_filter: Filter networks by status (e.g., 'ACTIVE', 'DOWN')
            shared_only: If True, only show shared networks

        Returns:
            List of Network objects
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
        Get detailed information about a specific Neutron network.

        Args:
            network_id: ID of the network to retrieve

        Returns:
            Network object with detailed information
        """
        conn = get_openstack_conn()

        network = conn.network.get_network(network_id)
        if not network:
            raise Exception(f"Network with ID {network_id} not found")

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
            raise Exception("No update parameters provided")

        network = conn.network.update_network(network_id, **update_args)

        return self._convert_to_network_model(network)

    def delete_network(self, network_id: str) -> None:
        """
        Delete a Neutron network.

        Args:
            network_id: ID of the network to delete

        Returns:
            None
        """
        conn = get_openstack_conn()

        network = conn.network.get_network(network_id)
        if not network:
            raise Exception(f"Network with ID {network_id} not found")

        conn.network.delete_network(network_id, ignore_missing=False)

        return None

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
        Get the list of Neutron subnets with optional filtering.
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
            if has_gateway:
                subnets = [
                    s for s in subnets if getattr(s, "gateway_ip", None)
                ]
            else:
                subnets = [
                    s for s in subnets if not getattr(s, "gateway_ip", None)
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
        Create a new Neutron subnet.
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
        Get detailed information about a specific Neutron subnet.
        """
        conn = get_openstack_conn()
        subnet = conn.network.get_subnet(subnet_id)
        if not subnet:
            raise Exception(f"Subnet with ID {subnet_id} not found")
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
        Update an existing Neutron subnet.
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
            raise Exception("No update parameters provided")
        subnet = conn.network.update_subnet(subnet_id, **update_args)
        return self._convert_to_subnet_model(subnet)

    def delete_subnet(self, subnet_id: str) -> None:
        """
        Delete a Neutron subnet.
        """
        conn = get_openstack_conn()
        subnet = conn.network.get_subnet(subnet_id)
        if not subnet:
            raise Exception(f"Subnet with ID {subnet_id} not found")
        conn.network.delete_subnet(subnet_id, ignore_missing=False)
        return None

    def set_subnet_gateway(self, subnet_id: str, gateway_ip: str) -> Subnet:
        conn = get_openstack_conn()
        subnet = conn.network.update_subnet(subnet_id, gateway_ip=gateway_ip)
        return self._convert_to_subnet_model(subnet)

    def clear_subnet_gateway(self, subnet_id: str) -> Subnet:
        conn = get_openstack_conn()
        subnet = conn.network.update_subnet(subnet_id, gateway_ip=None)
        return self._convert_to_subnet_model(subnet)

    def set_subnet_dhcp_enabled(self, subnet_id: str, enabled: bool) -> Subnet:
        conn = get_openstack_conn()
        subnet = conn.network.update_subnet(subnet_id, enable_dhcp=enabled)
        return self._convert_to_subnet_model(subnet)

    def toggle_subnet_dhcp(self, subnet_id: str) -> Subnet:
        conn = get_openstack_conn()
        current = conn.network.get_subnet(subnet_id)
        if not current:
            raise Exception(f"Subnet with ID {subnet_id} not found")
        subnet = conn.network.update_subnet(
            subnet_id,
            enable_dhcp=not bool(current.enable_dhcp),
        )
        return self._convert_to_subnet_model(subnet)

    def _convert_to_subnet_model(self, openstack_subnet) -> Subnet:
        """
        Convert an OpenStack subnet object to a Subnet pydantic model.
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
        Get the list of Neutron ports with optional filtering.
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
        conn = get_openstack_conn()
        port = conn.network.get_port(port_id)
        if not port:
            raise Exception(f"Port with ID {port_id} not found")
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
        conn = get_openstack_conn()
        port = conn.network.get_port(port_id)
        if not port:
            raise Exception(f"Port with ID {port_id} not found")
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
        conn = get_openstack_conn()
        port = conn.network.get_port(port_id)
        if not port:
            raise Exception(f"Port with ID {port_id} not found")
        return list(getattr(port, "allowed_address_pairs", []) or [])

    def add_port_allowed_address_pair(
        self,
        port_id: str,
        ip_address: str,
        mac_address: str | None = None,
    ) -> Port:
        conn = get_openstack_conn()
        port = conn.network.get_port(port_id)
        if not port:
            raise Exception(f"Port with ID {port_id} not found")
        pairs = list(getattr(port, "allowed_address_pairs", []) or [])
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
        conn = get_openstack_conn()
        port = conn.network.get_port(port_id)
        if not port:
            raise Exception(f"Port with ID {port_id} not found")
        pairs = list(getattr(port, "allowed_address_pairs", []) or [])

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
        conn = get_openstack_conn()
        update_args: dict = {}
        if host_id is not None:
            update_args["binding_host_id"] = host_id
        if vnic_type is not None:
            update_args["binding_vnic_type"] = vnic_type
        if profile is not None:
            update_args["binding_profile"] = profile
        if not update_args:
            raise Exception("No update parameters provided")
        updated = conn.network.update_port(port_id, **update_args)
        return self._convert_to_port_model(updated)

    def set_port_admin_state(
        self,
        port_id: str,
        is_admin_state_up: bool,
    ) -> Port:
        conn = get_openstack_conn()
        updated = conn.network.update_port(
            port_id,
            admin_state_up=is_admin_state_up,
        )
        return self._convert_to_port_model(updated)

    def toggle_port_admin_state(self, port_id: str) -> Port:
        conn = get_openstack_conn()
        current = conn.network.get_port(port_id)
        if not current:
            raise Exception(f"Port with ID {port_id} not found")
        updated = conn.network.update_port(
            port_id,
            admin_state_up=not bool(current.admin_state_up),
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
        Create a new Neutron port.
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
        Get detailed information about a specific Neutron port.
        """
        conn = get_openstack_conn()
        port = conn.network.get_port(port_id)
        if not port:
            raise Exception(f"Port with ID {port_id} not found")
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
        Update an existing Neutron port.
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
            raise Exception("No update parameters provided")
        port = conn.network.update_port(port_id, **update_args)
        return self._convert_to_port_model(port)

    def delete_port(self, port_id: str) -> None:
        """
        Delete a Neutron port.
        """
        conn = get_openstack_conn()
        port = conn.network.get_port(port_id)
        if not port:
            raise Exception(f"Port with ID {port_id} not found")
        conn.network.delete_port(port_id, ignore_missing=False)
        return None

    def _convert_to_port_model(self, openstack_port) -> Port:
        """
        Convert an OpenStack port object to a Port pydantic model.
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
        Get the list of Neutron floating IPs with optional filtering.
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
            ips = [i for i in ips if not getattr(i, "port_id", None)]
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
        Create a new Neutron floating IP.
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
        Allocate floating IP pool (external network access) to a project via RBAC.
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
        Attach a floating IP to a port.
        """
        conn = get_openstack_conn()
        update_args: dict = {"port_id": port_id}
        if fixed_ip_address is not None:
            update_args["fixed_ip_address"] = fixed_ip_address
        ip = conn.network.update_ip(floating_ip_id, **update_args)
        return self._convert_to_floating_ip_model(ip)

    def detach_floating_ip_from_port(self, floating_ip_id: str) -> FloatingIP:
        """
        Detach a floating IP from its port.
        """
        conn = get_openstack_conn()
        ip = conn.network.update_ip(floating_ip_id, port_id=None)
        return self._convert_to_floating_ip_model(ip)

    def delete_floating_ip(self, floating_ip_id: str) -> None:
        """
        Delete a Neutron floating IP.
        """
        conn = get_openstack_conn()
        ip = conn.network.get_ip(floating_ip_id)
        if not ip:
            raise Exception(f"Floating IP with ID {floating_ip_id} not found")
        conn.network.delete_ip(floating_ip_id, ignore_missing=False)
        return None

    def update_floating_ip_description(
        self,
        floating_ip_id: str,
        description: str | None,
    ) -> FloatingIP:
        conn = get_openstack_conn()
        ip = conn.network.update_ip(floating_ip_id, description=description)
        return self._convert_to_floating_ip_model(ip)

    def reassign_floating_ip_to_port(
        self,
        floating_ip_id: str,
        port_id: str,
        fixed_ip_address: str | None = None,
    ) -> FloatingIP:
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
        conn = get_openstack_conn()
        existing = list(
            conn.network.ips(floating_network_id=floating_network_id),
        )
        available = next(
            (i for i in existing if not getattr(i, "port_id", None)),
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
