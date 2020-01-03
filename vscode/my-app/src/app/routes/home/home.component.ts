import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent implements OnInit {
  isCollapsed = false;
  menus = [
    {
      key: '任务列表',
      data: [
        {
          name: '任务',
          url: '/home/showAll',
        }
      ]
    }, {
      key: '添加任务',
      data: [
        {
          name: '添加任务',
          url: '/home/upload',
        }
      ]
    }
  ];
  constructor() { }

  ngOnInit() {
  }

}
