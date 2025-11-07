import argparse, json, os

def load_config(config_input):
    if os.path.exists(config_input):
        with open(config_input, 'r') as config_file:
            return json.load(config_file)
    try:
        # If not a file, assume it's a JSON string and try to parse it
        return json.loads(config_input)
    except json.JSONDecodeError:
        raise ValueError("Config is not a valid file path or a JSON string.")

def load_template(template_input):
    if os.path.exists(template_input):
        with open(template_input, 'r') as template_file:
            return template_file.read()
    try:
        return str(template_input)
    except Exception:
        raise ValueError("Template is not a valid file path or string.")

def save_output(output_path, content):
    with open(output_path, 'w') as output_file:
        output_file.write(content)

def fill_template(config, template_content):
    """Replaces placeholders in the template content with config values."""
    output_content = template_content
    for key, value in config.items():        
        output_content = output_content.replace("{{"+key+"}}", str(value))
    return output_content

def main():
    """Parses arguments, orchestrates template filling, and handles output."""
    parser = argparse.ArgumentParser(description='Generate a file from a template and configuration.')
    parser.add_argument('--config', required=True, help='Path to the config file OR a JSON string.')
    parser.add_argument('--template', required=True, help='Path to the template file OR a JSON string.')
    parser.add_argument('--out', help='Path to the output file. If omitted, prints to stdout.')
    args = parser.parse_args()

    # 1. Load inputs
    config_data = load_config(args.config)
    template_content = load_template(args.template)

    # 2. Process template
    output_content = fill_template(config_data, template_content)

    # 3. Handle output
    if args.out:
        save_output(args.out, output_content)
    else:
        print(output_content)

if __name__ == '__main__':
    main()