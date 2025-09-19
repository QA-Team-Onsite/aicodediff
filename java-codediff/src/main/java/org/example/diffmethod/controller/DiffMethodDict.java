package org.example.diffmethod.controller;

import lombok.Data;
import lombok.Getter;
import lombok.Setter;

import java.util.List;
import java.util.Map;
@Getter
@Setter
@Data
public class DiffMethodDict {
    // Getter 和 Setter 方法
    private String methodPath;

    // 无参构造函数
    public DiffMethodDict() {}

    // 有参构造函数
    public DiffMethodDict(String methodPath) {
        this.methodPath = methodPath;
    }

}

