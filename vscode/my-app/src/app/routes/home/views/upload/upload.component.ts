import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormControl, FormGroup, Validators } from '@angular/forms';
import * as OSS from 'ali-oss';
import { UploadService } from '../../domain/upload.service';
// declare var SparkMD5: any;
// declare var OSS: any;

@Component({
  selector: 'app-upload',
  templateUrl: './upload.component.html',
  styleUrls: ['./upload.component.css']
})
export class UploadComponent implements OnInit {
  newUpload: any;
  file: any;
  client: any;
  url: any;
  validateForm: FormGroup;
  fileName = '暂无文件';
  submitForm(): void {
    // tslint:disable-next-line: forin
    for (const i in this.validateForm.controls) {
      this.validateForm.controls[i].markAsDirty();
      this.validateForm.controls[i].updateValueAndValidity();
    }
  }

  updateConfirmValidator(): void {
    /** wait for refresh value */
    Promise.resolve().then(() => this.validateForm.controls.checkPassword.updateValueAndValidity());
  }

  confirmationValidator = (control: FormControl): { [s: string]: boolean } => {
    if (!control.value) {
      return { required: true };
    } else if (control.value !== this.validateForm.controls.password.value) {
      return { confirm: true, error: true };
    }
    return {};
  }

  getCaptcha(e: MouseEvent): void {
    e.preventDefault();
  }

  constructor(
    private fb: FormBuilder,
    private uploadService: UploadService,
  ) {
    this.client = new OSS({
      accessKeyId: 'LTAI4Fuz4nAp9HhHrXiyWcuN',
      accessKeySecret: 'iC7loJL64t8b4stVihnNfliqBl0TN8',
      endpoint: 'oss-cn-hangzhou.aliyuncs.com',
      bucket: 'deepdraw-dbr',
    });
  }

  getUpload(e) {
    if (e.target.files[0]) {
      const file = e.target.files[0];
      console.log(file);
      this.newUpload = file;
      this.displayName(file.name);
      this.uploadFile(file);
      e.target.value = '';
      console.log(e.target.value);
    }
  }

  displayName(name: string) {
    console.log(name);
    if (name.length > 20) {
      console.log('max');
      const preName = name.slice(0, 5);
      const endName = name.slice(name.length - 10, name.length);
      const nowName = preName + '...' + endName;
      this.fileName = nowName;
    } else {
      this.fileName = name;
    }
  }

  uploadFile(file) {
    this.url = '';
    const fileTypes = this.newUpload.name.split('.');
    const fileType = fileTypes[fileTypes.length - 1];
    console.log(fileType);
    const storeAs = 'dbr_data/ai_batchproc/' + this.newUpload.name;
    this.client.multipartUpload(storeAs, file)
      .then((result) => {
        console.log(result);
        if (result.res.requestUrls[0].split('?')[0].length > 0) {
          this.url = result.res.requestUrls[0].split('?')[0];
          alert('文件上传成功');
        } else {
          this.url = 'wrong';
        }
        console.log('upload', this.url);
      });
  }
  ngOnInit() {
    this.validateForm = this.fb.group({
      name: [null, [Validators.required]],
      numbers: [60],
    });
  }
  onSubmit() {
    if (this.validateForm.status === 'VALID') {
      // tslint:disable-next-line: new-parens
      const formData = this.validateForm.value;
      const name = formData.name;
      const numbers = formData.numbers;
      console.log(formData.name);
      console.log(formData.numbers);
      if (this.url.length > 10) {
        console.log(this.url);
        const apiData = this.uploadService.uploadFile(this.url, name, numbers);
        apiData.subscribe((resData: any) => {
          console.log('sss', resData);
          if (resData.errorCode === 0) {
            alert('添加成功');
          } else {
            alert('文件名不能有中文');
          }
        });
      } else {
        alert('请等候文件上传');
      }

    } else {
      alert('请完整填写信息');
    }
  }

}
