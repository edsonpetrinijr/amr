
#!/bin/sh

# 获取脚本所在目录（兼容性写法）
script_dir=$(dirname "$0")
script_dir=$(cd "$script_dir" && pwd)
project_root=$(cd "$script_dir/../../../.." && pwd)

# 当前目录（.proto文件所在目录）
proto_root="$project_root/proto"

# 输出目录
output_x86="$script_dir/x86"
output_arm="$script_dir/arm"

# protoc可执行文件路径
protoc_x86_dir="$script_dir/x86/protoc-3.15.7/bin"
protoc_arm_dir="$script_dir/arm/protoc-23.3/bin"

# 检查protoc是否存在
if [ ! -f "$protoc_x86_dir/protoc" ]; then
    echo "Error: x86 version of protoc not found in $protoc_x86_dir"
    exit 1
fi
if [ ! -f "$protoc_arm_dir/protoc" ]; then
    echo "Error: ARM version of protoc not found in $protoc_arm_dir"
    exit 1
fi

# 确保输出目录存在
mkdir -p "$output_x86"
mkdir -p "$output_arm"

# 递归查找所有.proto文件（兼容性写法）
find "$proto_root" -name "*.proto" | while read proto_file; do
    # 计算相对路径
    rel_path=$(echo "$proto_file" | sed "s|^$proto_root/||")
    
    # 计算输出路径（去掉文件名部分）
    out_dir=$(dirname "$rel_path")
    
    # 如果是根目录下的文件
    if [ "$out_dir" = "." ]; then
        out_dir=""
    fi

    echo "scripts proto build: $rel_path"
    
    # 创建输出目录（保持原始目录结构）
    mkdir -p "$output_x86/$out_dir"
    mkdir -p "$output_arm/$out_dir"
    
    # 使用 x86 版本的 protoc
    # echo "[x86] 编译: $rel_path"
    (cd "$protoc_x86_dir" && \
        ./protoc --proto_path="$proto_root" --python_out="$output_x86/$out_dir" "$proto_file")
    if [ $? -eq 0 ]; then
        : # echo "[x86] 成功"
    else
        echo "[x86] failed"
        exit 1
    fi
    
    # 使用 ARM 版本的 protoc
    # echo "[ARM] 编译: $rel_path"
    (cd "$protoc_arm_dir" && \
        ./protoc --proto_path="$proto_root" --python_out="$output_arm/$out_dir" "$proto_file")
    if [ $? -eq 0 ]; then
        : # echo "[ARM] 成功"
    else
        echo "[ARM] failed"
        exit 1
    fi
done

echo "All .proto files processed (x86 + ARM)"