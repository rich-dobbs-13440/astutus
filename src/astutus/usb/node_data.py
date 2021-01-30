import astutus.usb


class NodeDataSearcher(object):

    def __init__(self):
        self.device_configurations = astutus.usb.DeviceConfigurations()
        self.aliases = astutus.usb.device_aliases.DeviceAliases(filepath=None)
        self.pci_device_info_map = astutus.util.pci.get_slot_to_device_info_map_from_lspci()
        self.node_data_by_dirpath = {}

    def get_node_data(self, dirpath):
        parent_dirpath, dirname = dirpath.rsplit('/', 1)
        ilk = astutus.usb.usb_impl.find_ilk_for_dirpath(dirpath)
        if ilk == 'pci':
            pci_device_info = astutus.util.pci.get_device_info_from_dirname(self.pci_device_info_map, dirname)
        else:
            pci_device_info = None
        data_for_dirpath = astutus.usb.tree.get_data_for_dirpath(ilk, dirpath, pci_device_info)
        nodeid = data_for_dirpath['node_id']
        # With the nodeid, it is possible to get the configuration
        device_config = self.device_configurations.get_item_from_nodeid(nodeid)
        # With the nodeid, can assemble the nodepath
        parent_node_data = self.node_data_by_dirpath.get(parent_dirpath)
        if parent_node_data is None:
            if parent_dirpath == '/sys':
                parent_node_data = None
                parent_nodepath = ""
            else:
                parent_node_data = self.get_node_data(parent_dirpath)
                parent_nodepath = parent_node_data.get('nodepath')
        if parent_nodepath == "":
            nodepath = nodeid
        else:
            nodepath = parent_nodepath + '/' + nodeid
        # With the nodepath, the alias can be found
        alias = self.aliases.find_highest_priority(nodepath)
        node_data = astutus.usb.tree.get_node_data(data_for_dirpath, device_config, alias)

        return {
            'dirpath': dirpath,
            'dirname': dirname,
            'ilk': ilk,
            'pci_device_info': pci_device_info,
            'data_for_dirpath': data_for_dirpath,
            'nodeid': nodeid,
            'device_config': device_config,
            'html_label': node_data['html_label'],
            'nodepath': nodepath,
            'alias': alias,
            'node_data': node_data,
        }
