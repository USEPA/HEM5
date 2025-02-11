import os


class Directory:

    @staticmethod
    def find_facilities(output_dir):
        files = os.listdir(output_dir)
        root_path = output_dir + '/'

        return [item for item in files if os.path.isdir(os.path.join(root_path, item))
                and 'inputs' not in item.lower() and 'acute maps' not in item.lower()
                and 'pop' not in item.lower()]