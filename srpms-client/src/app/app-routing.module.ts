import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';

import { HomeComponent } from './home/home.component';
import { ContractComponent } from './contract/contract.component';
import {ContractMgtComponent} from './contract-mgt/contract-mgt.component';
import {ContractViewerComponent} from './contract-viewer/contract-viewer.component';

const routes: Routes = [
  { path: '', component: HomeComponent },
  { path: 'contract', component: ContractComponent },
  { path: 'supervise', component: ContractMgtComponent },
  { path: 'contract-viewer', component: ContractViewerComponent },
  { path: 'examine', component: ContractMgtComponent },
  { path: 'submit', component: ContractMgtComponent },
  { path: 'convene', component: ContractMgtComponent },
  { path: 'nonformal', component: ContractMgtComponent },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
