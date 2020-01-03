import { Component, OnInit } from '@angular/core';
import { TasksService } from '../../domain/tasks.service';


@Component({
  selector: 'app-show-all',
  templateUrl: './show-all.component.html',
  styleUrls: ['./show-all.component.css']
})
export class ShowAllComponent implements OnInit {
  taskList: any;
  numbers = 1;
  status: 'stop';
  isStartVisible = false;
  isDeleteVisible = false;
  isStopVisible = false;
  newTask: any;
  constructor(
    private taskService: TasksService,
  ) {
    this.getTasks();
  }


  ngOnInit() {
    this.getTasks();

  }

  getTasks() {
    this.taskService.getTasks().subscribe((api: any) => {
      console.log('api', api);
      if (api.view_list) {
        this.taskList = api.view_list;
      } else {
        alert('查找失败');
      }
      console.log(this.taskList);
    });
  }

  onStart(task: any) {
    this.isStartVisible = true;
    this.newTask = task;
  }

  onDelete(task: any) {
    this.newTask = task;

    this.isDeleteVisible = true;
  }

  onStop(task: any) {
    this.newTask = task;
    this.isStopVisible = true;
  }

  handleStartCancel() {
    this.isStartVisible = false;
  }

  handleStartOk(task: any) {
    console.log('aa', task);
    this.taskService.startTask(task, this.numbers).subscribe((res: any) => {
      if (res.errorCode === 0) {
      } else {
        alert('开始失败');
      }
      this.getTasks();
    });
  }

  handleDeleteOk(task: any) {
    console.log('bb', task);
    this.taskService.deleteTask(task).subscribe((res: any) => {
      if (res.errorCode === 0) {
        this.isDeleteVisible = false;
        alert('删除成功');
      } else {
        alert('删除失败');
      }
      this.getTasks();
    });
  }

  handleDeleteCancel() {
    this.isDeleteVisible = false;
  }

  handleStopOk(task: any) {
    console.log('cc', task);
    this.taskService.stopTask(task).subscribe((res: any) => {
      if (res.errorCode === 0) {
        alert('停止成功');
        this.getTasks();
      } else {
        alert('停止失败');
      }
      this.getTasks();

    });
  }

  handleStopCancel() {
    this.isDeleteVisible = false;
  }

}
