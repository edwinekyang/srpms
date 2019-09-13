import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { HomeComponent } from './home/home.component';
import { ContractComponent } from './contract/contract.component';
import {FormsModule, ReactiveFormsModule} from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';
import { SidenavComponent } from './sidenav/sidenav.component';
import { MatGridListModule } from '@angular/material/grid-list';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatButtonModule } from '@angular/material/button';
import { MatListModule } from '@angular/material/list';
import { HeaderComponent } from './header/header.component';
import { MatCardModule } from '@angular/material/card';
import { ContractFormComponent } from './contract-form/contract-form.component';
import { ContractFormElementComponent } from './contract-form-element/contract-form-element.component';

@NgModule({
  declarations: [
    AppComponent,
    HomeComponent,
    ContractComponent,
    SidenavComponent,
    HeaderComponent,
    ContractFormComponent,
    ContractFormElementComponent
  ],
    imports: [
        BrowserModule,
        BrowserAnimationsModule,
        AppRoutingModule,
        FormsModule,
        HttpClientModule,
        MatGridListModule,
        MatSidenavModule,
        MatButtonModule,
        MatListModule,
        MatCardModule,
        ReactiveFormsModule
    ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
