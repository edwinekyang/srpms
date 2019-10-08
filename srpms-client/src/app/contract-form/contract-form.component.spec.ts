import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ContractFormComponent } from './contract-form.component';
import {CUSTOM_ELEMENTS_SCHEMA} from '@angular/core';
import {FormsModule, ReactiveFormsModule} from '@angular/forms';
import {HttpClient} from '@angular/common/http';
import {HttpClientTestingModule, HttpTestingController} from '@angular/common/http/testing';
import {MatDialog} from '@angular/material';
import {RouterTestingModule} from '@angular/router/testing';

describe('ContractFormComponent', () => {
  let component: ContractFormComponent;
  let fixture: ComponentFixture<ContractFormComponent>;
  let httpClient: HttpClient;
  let httpTestingController: HttpTestingController;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      imports: [
          HttpClientTestingModule,
          FormsModule,
          ReactiveFormsModule,
          RouterTestingModule,
      ],
      declarations: [ ContractFormComponent ],
      schemas: [CUSTOM_ELEMENTS_SCHEMA],
      providers: [
        { provide: MatDialog, useValue: {} }
        ],
    })
    .compileComponents();

    // Inject the http service and test controller for each test
    httpClient = TestBed.get(HttpClient);
    httpTestingController = TestBed.get(HttpTestingController);
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ContractFormComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
