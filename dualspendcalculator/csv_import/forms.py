from django import forms


class CSVUploadForm(forms.Form):
    """CSVアップロードフォーム"""
    
    csv_file = forms.FileField(
        label="CSVファイル",
        widget=forms.FileInput(attrs={
            "class": "form-input",
            "accept": ".csv",
        }),
    )

    def clean_csv_file(self):
        csv_file = self.cleaned_data.get("csv_file")
        
        if csv_file:
            # ファイルサイズチェック（5MB上限）
            if csv_file.size > 5 * 1024 * 1024:
                raise forms.ValidationError("ファイルサイズは5MB以下にしてください")
            
            # 拡張子チェック
            if not csv_file.name.lower().endswith(".csv"):
                raise forms.ValidationError("CSVファイルを選択してください")
        
        return csv_file

