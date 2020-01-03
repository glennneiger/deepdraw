import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams, HttpErrorResponse } from '@angular/common/http';
@Injectable({
  providedIn: 'root'
})
export class UploadService {

  constructor(
    private httpClient: HttpClient,
  ) { }

  uploadFile(taskFile,name, batch) {
    const op = { task_name: name, task_file: taskFile, batch_size: batch };
    return this.httpClient.put('http://192.168.2.114:8081/polls/task/', {
      'task_name': name,
      'task_file': taskFile,
      'batch_size': batch
    });
  }
}
