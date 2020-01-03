import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { UploadComponent } from './views/upload/upload.component';
import { ShowAllComponent } from './views/show-all/show-all.component';
import { HomeComponent } from './home.component';


const routes: Routes = [
  {
    path: '',
    component: HomeComponent,
    children:
      [
        {
          path: 'upload',
          component: UploadComponent,
        },
        {
          path: 'showAll',
          component: ShowAllComponent,
        },
      ]
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class HomeRoutingModule { }
