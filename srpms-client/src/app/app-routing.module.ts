import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';

import { HomeComponent } from './home/home.component';
import { ContractComponent } from './contract/contract.component';
import {SupervisorComponent} from './supervisor/supervisor.component';

const routes: Routes = [
  { path: '', component: HomeComponent },
  { path: 'contract', component: ContractComponent },
  { path: 'supervisor', component: SupervisorComponent },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
