import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';

import { HomeComponent } from './home/home.component';
import { ContractComponent } from './contract/contract.component';
import {SupervisorComponent} from './supervisor/supervisor.component';
import {ContractViewerComponent} from './contract-viewer/contract-viewer.component';

const routes: Routes = [
  { path: '', component: HomeComponent },
  { path: 'contract', component: ContractComponent },
  { path: 'supervisor', component: SupervisorComponent },
  { path: 'contract-viewer', component: ContractViewerComponent },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
