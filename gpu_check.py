import subprocess
import platform


def check_gpu_availability():
    """
    Check if the machine has GPUs available.
    
    Returns:
        dict: Dictionary containing GPU information with keys:
            - has_gpu (bool): Whether GPUs are detected
            - gpu_count (int): Number of GPUs found
            - gpu_info (list): List of GPU details
            - method (str): Detection method used
    """
    result = {
        'has_gpu': False,
        'gpu_count': 0,
        'gpu_info': [],
        'method': None
    }
    
    # Try NVIDIA GPUs first
    try:
        output = subprocess.check_output(['nvidia-smi', '-L'], 
                                       stderr=subprocess.DEVNULL, 
                                       universal_newlines=True)
        gpu_lines = [line.strip() for line in output.split('\n') if line.strip().startswith('GPU')]
        result['has_gpu'] = len(gpu_lines) > 0
        result['gpu_count'] = len(gpu_lines)
        result['gpu_info'] = gpu_lines
        result['method'] = 'nvidia-smi'
        return result
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    # Try PyTorch if available
    try:
        import torch
        if torch.cuda.is_available():
            result['has_gpu'] = True
            result['gpu_count'] = torch.cuda.device_count()
            result['gpu_info'] = [torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())]
            result['method'] = 'pytorch'
            return result
    except ImportError:
        pass
    
    # Try system-specific methods
    system = platform.system().lower()
    
    if system == 'darwin':  # macOS
        try:
            output = subprocess.check_output(['system_profiler', 'SPDisplaysDataType'], 
                                           stderr=subprocess.DEVNULL, 
                                           universal_newlines=True)
            if 'Chipset Model:' in output:
                gpu_lines = []
                for line in output.split('\n'):
                    if 'Chipset Model:' in line:
                        gpu_lines.append(line.strip())
                result['has_gpu'] = len(gpu_lines) > 0
                result['gpu_count'] = len(gpu_lines)
                result['gpu_info'] = gpu_lines
                result['method'] = 'system_profiler'
                return result
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
    
    elif system == 'linux':
        try:
            output = subprocess.check_output(['lspci'], 
                                           stderr=subprocess.DEVNULL, 
                                           universal_newlines=True)
            gpu_lines = [line for line in output.split('\n') if 'VGA' in line or 'Display' in line]
            result['has_gpu'] = len(gpu_lines) > 0
            result['gpu_count'] = len(gpu_lines)
            result['gpu_info'] = gpu_lines
            result['method'] = 'lspci'
            return result
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
    
    return result


if __name__ == "__main__":
    gpu_info = check_gpu_availability()
    
    print("GPU Detection Results:")
    print(f"Has GPU: {gpu_info['has_gpu']}")
    print(f"GPU Count: {gpu_info['gpu_count']}")
    print(f"Detection Method: {gpu_info['method']}")
    
    if gpu_info['gpu_info']:
        print("GPU Details:")
        for i, gpu in enumerate(gpu_info['gpu_info']):
            print(f"  {i+1}: {gpu}")
    else:
        print("No GPUs detected")