
class RegistryParser():

    def __init__(self, base, registry):
        self.base = base
        self.registry = registry
        self.id = self.registry['id_reg']
        del self.registry['id_reg']

    def get_base(self, base, attr):
        for content in base['content']:
            if content.get('field'):
                field = content['field']
                if field['name'] == attr:
                    return field
            elif content.get('group'):
                group = content['group']
                if group['metadata']['name'] == attr:
                    return group
        raise Exception('Structure "%s" is not present in base definitions.' % attr)

    def destroy_field(self, base, registry, field):
        if 'Nenhum' in base.get('indices', []):
            del registry[field]
            return True
        return False

    def parse(self, base=None, registry=None):
        """ Receives base json (dict) and registry (dict).
            Will search fileds in registry that are setted 
            with "NoIndex" in base structure, and then
            will delete it from registry, so it will not
            be indexed.
        """
        if not registry: registry = self.registry
        if not base: base = self.base

        _registry = registry.copy()

        for attr in _registry:

            value = _registry[attr]
            _base = self.get_base(base, attr)

            if type(value) is dict and not utils.is_file_mask(value):
                self.parse(_base, value)

            elif type(value) is list:

                if not self.destroy_field(_base, registry, attr):
                    for item in value:
                        if type(item) is dict:
                            self.parse(_base, item)
            else:
                _base = self.get_base(base, attr)
                self.destroy_field(_base, registry, attr)

        return self.registry


