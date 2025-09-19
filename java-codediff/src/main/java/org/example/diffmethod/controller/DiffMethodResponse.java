package org.example.diffmethod.controller;

import java.util.Map;
import lombok.Data;
import lombok.Getter;
import lombok.Setter;

import java.util.List;
import java.util.Map;
@Getter
@Setter
@Data
public class DiffMethodResponse {
    private int code;
    private String clazz;
    private Map<String, MethodInfo> methods;

}
