from flask import Flask, render_template, jsonify, request, send_file
import re
import os

app = Flask(__name__)

def extract_amount(text):
    # 移除所有空格
    text = text.replace(' ', '')
    
    # 初始化金额列表
    amounts = []
    calculation = []
    
    # 新增：处理以下划线分隔的文件名格式
    if '_' in text:
        parts = text.split('_')
        for part in parts:
            if part.endswith('元'):
                try:
                    amount = float(part.replace('元', ''))
                    amounts.append(amount)
                    calculation.append(f"{amount}")
                except ValueError:
                    continue
    
    # 原有的金额提取规则
    # 匹配金额模式：数字（可能包含小数点）后跟"元"
    pattern = r'(\d+(?:\.\d+)?)元'
    matches = re.findall(pattern, text)
    
    for match in matches:
        try:
            amount = float(match)
            if amount not in amounts:  # 避免重复添加
                amounts.append(amount)
                calculation.append(f"{amount}")
        except ValueError:
            continue
    
    # 如果没有找到任何金额，返回0
    if not amounts:
        return 0, [], 0
    
    # 计算总金额
    total_amount = sum(amounts)
    
    return amounts, calculation, total_amount

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/preview/<path:filename>')
def preview_file(filename):
    # 构造文件的完整路径
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    try:
        return send_file(file_path)
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@app.route('/process', methods=['POST'])
def process():
    files = request.json.get('files', [])
    
    if not files or len(files) > 100:
        return jsonify({
            'error': '请上传1-100个文件'
        }), 400
        
    total_amount = 0
    amounts = []
    results = []
    calculation = []
    failed_files = []  # 存储未成功提取金额的文件
    
    # 统计信息
    total_files = len(files)
    
    for filename in files:
        file_amounts, file_calculation, file_total_amount = extract_amount(filename)
        
        if file_amounts:
            for amount in file_amounts:
                amounts.append(amount)
                calculation.append(f"{amount}")
                results.append({
                    'filename': filename,
                    'amount': amount
                })
            total_amount += file_total_amount
        else:
            # 如果没有提取到金额，添加到失败列表
            failed_files.append(filename)
    
    # 计算成功和失败的文件数
    success_files = total_files - len(failed_files)
    
    calculation_str = ' + '.join(calculation) if calculation else "0"
    
    return jsonify({
        'results': results,
        'calculation': calculation_str,
        'total': total_amount,
        'failed_files': failed_files,
        'stats': {
            'total_files': total_files,
            'success_files': success_files,
            'failed_files': len(failed_files)
        }
    })

if __name__ == '__main__':
    app.run(debug=True, port=5006)
