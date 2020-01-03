import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class TasksService {

  constructor(
    private httpClient: HttpClient,
  ) { }

  getTasks() {
    return this.httpClient.post('http://192.168.2.114:8081/polls/tasksummary/', {});
  }

  stopTask(task: any) {
    const options = { option: 'stop', 'task_name': task.task_name };
    return this.httpClient.post(' http://192.168.2.114:8081/polls/task/', options);
  }
  startTask(task: any, numbers: number) {
    console.log(numbers, 'number');
    console.log(task.task_name);
    const options = { option: 'start', task_name: task.task_name, retry_num: numbers, stop_thre: 50 };
    return this.httpClient.post('http://192.168.2.114:8081/polls/task/', options);
  }
  deleteTask(task: any) {
    const options = { params: new HttpParams({ fromObject: { task_name: task.task_name } }) };
    return this.httpClient.delete('http://192.168.2.114:8081/polls/task/', options);
  }
}
