import collections


class Generator:
    def __init__(self):
        manifest_format = collections.OrderedDict([
            ("type", "datasafe dataset manifest"),
            ("version", "0.1.0.dev4"),
        ])
        manifest_dataset = collections.OrderedDict([
            ("loi", ""),
            ("complete", False),
        ])
        manifest_files = collections.OrderedDict([
            ("metadata", []),
            ("data", None),
            ("checksums", []),
        ])
        manifest_keys_level_one = [
            ('format', manifest_format),
            ('dataset', manifest_dataset),
            ('files', manifest_files),
        ]
        self.manifest = collections.OrderedDict(manifest_keys_level_one)
        self.filename = 'MANIFEST.yaml'

    def populate(self):
        pass

    def write(self):
        with open(self.filename, mode='w+') as output_file:
            output_file.write('')
