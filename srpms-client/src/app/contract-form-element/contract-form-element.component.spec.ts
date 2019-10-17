import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ContractFormElementComponent } from './contract-form-element.component';
import { CUSTOM_ELEMENTS_SCHEMA } from '@angular/core';
import { FormBuilder, FormControl, FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatDatepickerModule, MatAutocompleteModule } from '@angular/material';

describe('ContractFormElementComponent', () => {
  let component: ContractFormElementComponent;
  let fixture: ComponentFixture<ContractFormElementComponent>;

  // create new instance of FormBuilder
  const formBuilder: FormBuilder = new FormBuilder();

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      imports: [ FormsModule, ReactiveFormsModule, MatDatepickerModule, MatAutocompleteModule ],
      declarations: [ ContractFormElementComponent ],
      schemas: [ CUSTOM_ELEMENTS_SCHEMA ]
    })
      .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ContractFormElementComponent);
    component = fixture.componentInstance;
    component.form = formBuilder.group({
      valid: new FormControl()
    });
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
