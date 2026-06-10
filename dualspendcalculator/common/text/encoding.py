"""
文字コード処理

ファイルの文字コード判定機能を提供する。
"""


def detect_encoding(file_content: bytes) -> str:
    """
    ファイルの文字コードを自動判定する
    
    判定順序:
    1. UTF-8 BOMの有無を確認
    2. UTF-8としてデコードを試行
    3. CP932（Shift-JIS）としてデコードを試行
    
    Args:
        file_content: ファイルのバイナリ内容
        
    Returns:
        検出された文字コード名（"utf-8-sig", "utf-8", "cp932"）
        
    Raises:
        ValueError: 文字コードを認識できない場合
        
    使用例:
        >>> with open("file.csv", "rb") as f:
        ...     encoding = detect_encoding(f.read())
        >>> text = content.decode(encoding)
    """
    # UTF-8 BOMチェック
    if file_content.startswith(b'\xef\xbb\xbf'):
        return "utf-8-sig"
    
    # UTF-8としてデコードを試行
    try:
        file_content.decode("utf-8")
        return "utf-8"
    except UnicodeDecodeError:
        pass
    
    # CP932としてデコードを試行
    try:
        file_content.decode("cp932")
        return "cp932"
    except UnicodeDecodeError:
        pass
    
    raise ValueError("ファイルの文字コードを認識できません。CP932またはUTF-8で保存してください")

