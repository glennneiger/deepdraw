import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { NgZorroAntdModule } from 'ng-zorro-antd';
import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { HomeRoutingModule } from './home-routing.module';
import { UploadComponent } from './views/upload/upload.component';
import { BrowserModule } from '@angular/platform-browser';
import { ShowAllComponent } from './views/show-all/show-all.component';
import { HomeComponent } from './home.component';


@NgModule({
  declarations: [
    UploadComponent,
    ShowAllComponent,
    HomeComponent
  ],
  imports: [
    CommonModule,
    HomeRoutingModule,
    NgZorroAntdModule,
    FormsModule,
    ReactiveFormsModule,
  ]
})
export class HomeModule { }
