from .config import KEY_MAPPER


class KeyMapper:
    """Mapper class for transforming JSON data keys per configuration."""

    @staticmethod
    def transform_keys(data: list) -> list:
        """Transform keys in JSON data per KEY_MAPPER configuration.

        Args:
            data (list): The JSON data to transform. Must be a list of
                dictionaries.

        Returns:
            list: JSON data with transformed keys.

        Raises:
            ValueError: If data is None or invalid.
        """
        if data is None:
            raise ValueError("Data cannot be None. Provide valid JSON data.")

        transformed_data = []
        for item in data:
            transformed_item = {}

            # Map keys according to KEY_MAPPER configuration
            for old_key, new_key in KEY_MAPPER.items():
                if old_key in item:
                    transformed_item[new_key] = item[old_key]

            # Preserve the index field if it exists
            if "index" in item:
                transformed_item["index"] = item["index"]

            transformed_data.append(transformed_item)

        return transformed_data
